"""
Vector Store Service for RAG
Manages FAISS and ChromaDB vector stores for semantic search
"""

import os
import pickle
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Literal
import faiss
import numpy as np
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from app.config import settings


VectorStoreType = Literal["faiss", "chromadb"]


class VectorStoreService:
    """
    Service for managing vector stores (FAISS and ChromaDB)
    Provides unified interface for storing and retrieving embeddings
    """

    def __init__(
        self,
        store_type: VectorStoreType = "faiss",
        store_name: str = "default",
        embedding_dimension: int = 1536,
        embeddings: Optional[Embeddings] = None,
    ):
        """
        Initialize vector store service

        Args:
            store_type: Type of vector store (faiss, chromadb)
            store_name: Name identifier for the store
            embedding_dimension: Dimension of embeddings
            embeddings: LangChain embeddings instance (required for ChromaDB)
        """
        self.store_type = store_type
        self.store_name = store_name
        self.embedding_dimension = embedding_dimension
        self.embeddings = embeddings

        # Storage paths
        self.base_path = Path("data/vector_stores")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.store_path = self.base_path / store_name

        # Initialize store
        if store_type == "faiss":
            self.index, self.id_map = self._init_faiss()
        elif store_type == "chromadb":
            self.vectorstore = self._init_chromadb()
        else:
            raise ValueError(f"Unsupported store type: {store_type}")

    def _init_faiss(self) -> Tuple[faiss.IndexFlatL2, Dict[int, str]]:
        """
        Initialize or load FAISS index

        Returns:
            Tuple of (FAISS index, ID map)
        """
        index_path = self.store_path / "faiss.index"
        id_map_path = self.store_path / "id_map.pkl"

        if index_path.exists() and id_map_path.exists():
            # Load existing index
            index = faiss.read_index(str(index_path))
            with open(id_map_path, "rb") as f:
                id_map = pickle.load(f)
        else:
            # Create new index
            self.store_path.mkdir(parents=True, exist_ok=True)
            index = faiss.IndexFlatL2(self.embedding_dimension)
            id_map = {}

        return index, id_map

    def _init_chromadb(self) -> Chroma:
        """
        Initialize or load ChromaDB store

        Returns:
            ChromaDB vectorstore
        """
        if not self.embeddings:
            raise ValueError("Embeddings instance required for ChromaDB")

        self.store_path.mkdir(parents=True, exist_ok=True)

        return Chroma(
            collection_name=self.store_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.store_path),
        )

    def add_embeddings(
        self,
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Add embeddings to vector store

        Args:
            embeddings: List of embedding vectors
            ids: List of unique IDs for each embedding
            metadatas: Optional metadata for each embedding
        """
        if self.store_type == "faiss":
            self._add_to_faiss(embeddings, ids)
        elif self.store_type == "chromadb":
            self._add_to_chromadb(embeddings, ids, metadatas)

    def _add_to_faiss(self, embeddings: List[List[float]], ids: List[str]) -> None:
        """Add embeddings to FAISS index"""
        embeddings_array = np.array(embeddings, dtype=np.float32)

        # Add to index
        start_idx = self.index.ntotal
        self.index.add(embeddings_array)

        # Update ID map
        for i, doc_id in enumerate(ids):
            self.id_map[start_idx + i] = doc_id

        # Save index
        self.save()

    def _add_to_chromadb(
        self,
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]],
    ) -> None:
        """Add embeddings to ChromaDB"""
        # ChromaDB requires text content, use IDs as placeholder if no metadata
        texts = [meta.get("content", id_val) for meta, id_val in zip(metadatas or [{} for _ in ids], ids)]

        self.vectorstore.add_texts(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas or [{"id": id_val} for id_val in ids],
            ids=ids,
        )

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Add documents with their embeddings to the store

        Args:
            texts: Document texts
            embeddings: Pre-computed embeddings
            ids: Document IDs
            metadatas: Optional metadata
        """
        if self.store_type == "chromadb":
            # ChromaDB handles this directly
            self.vectorstore.add_texts(
                texts=texts,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas,
            )
        else:
            # FAISS stores embeddings only, metadata managed separately
            self._add_to_faiss(embeddings, ids)

    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Search for similar documents

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return

        Returns:
            List of (document_id, similarity_score) tuples
        """
        if self.store_type == "faiss":
            return self._search_faiss(query_embedding, k)
        elif self.store_type == "chromadb":
            return self._search_chromadb(query_embedding, k)
        else:
            return []

    def _search_faiss(
        self,
        query_embedding: List[float],
        k: int,
    ) -> List[Tuple[str, float]]:
        """Search FAISS index"""
        query_array = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_array, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx in self.id_map:
                # Convert L2 distance to similarity score (lower is better)
                # Normalize to 0-1 range where 1 is most similar
                similarity = 1 / (1 + float(dist))
                results.append((self.id_map[idx], similarity))

        return results

    def _search_chromadb(
        self,
        query_embedding: List[float],
        k: int,
    ) -> List[Tuple[str, float]]:
        """Search ChromaDB"""
        results = self.vectorstore.similarity_search_by_vector(
            embedding=query_embedding,
            k=k,
        )

        # ChromaDB returns Document objects
        return [(doc.metadata.get("id", ""), 1.0) for doc in results]

    def delete_by_ids(self, ids: List[str]) -> None:
        """
        Delete documents by IDs

        Args:
            ids: List of document IDs to delete
        """
        if self.store_type == "faiss":
            # FAISS doesn't support direct deletion, would need rebuild
            # For now, we'll just remove from ID map
            indices_to_remove = [
                idx for idx, doc_id in self.id_map.items() if doc_id in ids
            ]
            for idx in indices_to_remove:
                del self.id_map[idx]
            self.save()

        elif self.store_type == "chromadb":
            self.vectorstore.delete(ids=ids)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if self.store_type == "faiss":
            return {
                "total_vectors": self.index.ntotal,
                "dimension": self.embedding_dimension,
                "store_type": "faiss",
            }
        elif self.store_type == "chromadb":
            collection = self.vectorstore._collection
            return {
                "total_vectors": collection.count(),
                "dimension": self.embedding_dimension,
                "store_type": "chromadb",
            }
        return {}

    def save(self) -> None:
        """Persist vector store to disk"""
        if self.store_type == "faiss":
            self.store_path.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.store_path / "faiss.index"))
            with open(self.store_path / "id_map.pkl", "wb") as f:
                pickle.dump(self.id_map, f)

        # ChromaDB auto-persists

    def clear(self) -> None:
        """Clear all data from vector store"""
        if self.store_type == "faiss":
            self.index, self.id_map = self._init_faiss()
            # Delete files
            index_path = self.store_path / "faiss.index"
            id_map_path = self.store_path / "id_map.pkl"
            if index_path.exists():
                index_path.unlink()
            if id_map_path.exists():
                id_map_path.unlink()

        elif self.store_type == "chromadb":
            # Recreate collection
            self.vectorstore = self._init_chromadb()

    def __repr__(self) -> str:
        return f"VectorStoreService(type={self.store_type}, name={self.store_name})"
