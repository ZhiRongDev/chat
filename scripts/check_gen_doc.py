from google import genai

# 1. Initialize Client
client = genai.Client(api_key="")

print("--- Checking File Stores & Contents ---\n")

# 2. List all File Search Stores
stores = list(client.file_search_stores.list())

if not stores:
    print("No File Search Stores found.")
else:
    for store in stores:
        print(f"📂 STORE: {store.display_name}")
        print(f"   ID:    {store.name}")

        # 3. List documents INSIDE this specific store
        # The 'parent' argument must be the store's unique name (ID)
        try:
            docs = list(client.file_search_stores.documents.list(parent=store.name))

            if not docs:
                print("   (Empty: No documents indexed)")
            else:
                for doc in docs:
                    # 'display_name' is the name you gave it (e.g., 'resume.pdf')
                    # 'name' is the internal ID (e.g., 'fileSearchStores/xxx/documents/yyy')
                    print(f"   - 📄 Document: {doc.display_name}")
                    print(f"     ID: {doc.name}")

        except Exception as e:
            print(f"   [Error listing docs: {e}]")

        print("-" * 40)
