from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class ChatSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatSessionCreate(BaseModel):
    title: str = "Yeni Sohbet"

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageCreate(BaseModel):
    session_id: str
    content: str

class ChatResponse(BaseModel):
    user_message: Message
    assistant_message: Message


# Routes
@api_router.get("/")
async def root():
    return {"message": "TürkGPT API"}

@api_router.post("/sessions", response_model=ChatSession)
async def create_session(input: ChatSessionCreate):
    """Yeni bir sohbet oturumu oluşturur"""
    session = ChatSession(**input.model_dump())
    doc = session.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.chat_sessions.insert_one(doc)
    return session

@api_router.get("/sessions", response_model=List[ChatSession])
async def get_sessions():
    """Tüm sohbet oturumlarını getirir"""
    sessions = await db.chat_sessions.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for session in sessions:
        if isinstance(session['created_at'], str):
            session['created_at'] = datetime.fromisoformat(session['created_at'])
    return sessions

@api_router.get("/sessions/{session_id}/messages", response_model=List[Message])
async def get_messages(session_id: str):
    """Belirli bir oturumdaki mesajları getirir"""
    messages = await db.messages.find({"session_id": session_id}, {"_id": 0}).sort("timestamp", 1).to_list(1000)
    for message in messages:
        if isinstance(message['timestamp'], str):
            message['timestamp'] = datetime.fromisoformat(message['timestamp'])
    return messages

@api_router.post("/chat", response_model=ChatResponse)
async def send_message(input: MessageCreate):
    """Kullanıcı mesajı gönderir ve GPT-5'ten cevap alır"""
    try:
        # Kullanıcı mesajını kaydet
        user_msg = Message(
            session_id=input.session_id,
            role="user",
            content=input.content
        )
        user_doc = user_msg.model_dump()
        user_doc['timestamp'] = user_doc['timestamp'].isoformat()
        await db.messages.insert_one(user_doc)
        
        # Önceki mesajları getir (context için)
        previous_messages = await db.messages.find(
            {"session_id": input.session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(100)
        
        # LLM ile sohbet et
        llm_key = os.environ.get('EMERGENT_LLM_KEY')
        chat = LlmChat(
            api_key=llm_key,
            session_id=input.session_id,
            system_message="Sen TürkGPT'sin, Türkçe konuşan yardımsever bir yapay zeka asistanısın. Her zaman kibar, bilgili ve dostça bir şekilde yanıt verirsin."
        )
        # Daha hızlı yanıt için gpt-4o-mini kullan
        chat.with_model("openai", "gpt-4o-mini")
        
        # Kullanıcı mesajını gönder
        user_message = UserMessage(text=input.content)
        response = await chat.send_message(user_message)
        
        # Asistan mesajını kaydet
        assistant_msg = Message(
            session_id=input.session_id,
            role="assistant",
            content=response
        )
        assistant_doc = assistant_msg.model_dump()
        assistant_doc['timestamp'] = assistant_doc['timestamp'].isoformat()
        await db.messages.insert_one(assistant_doc)
        
        return ChatResponse(
            user_message=user_msg,
            assistant_message=assistant_msg
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Mesaj gönderilemedi: {str(e)}")

@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Bir sohbet oturumunu ve mesajlarını siler"""
    await db.messages.delete_many({"session_id": session_id})
    result = await db.chat_sessions.delete_one({"id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı")
    return {"message": "Oturum silindi"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
