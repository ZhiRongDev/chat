from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
from app.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)

nonauth_router = APIRouter(prefix="/chat", tags=["chat"])


class ChatPayload(BaseModel):
    message: str


@nonauth_router.post("/")
async def chat_stream(payload: ChatPayload):
    user_message = payload.message

    if not user_message:
        raise HTTPException(status_code=400, detail="Missing 'message' field")

    async def stream_messages():
        response = client.models.generate_content_stream(
            model="gemini-2.5-flash", contents=[user_message]
        )

        for chunk in response:
            if chunk["text"]:
                text = chunk["text"]
                print(text, flush=True)
                yield text.encode("utf-8")  # ✅ yield bytes, not str

    return StreamingResponse(stream_messages(), media_type="text/plain")
