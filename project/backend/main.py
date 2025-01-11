# project/backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models.base import SessionLocal, engine
from models import models
from utils.llm import ModelInterface
from pydantic import BaseModel
from typing import List
import uvicorn

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="I-AM API")
llm = ModelInterface()

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    role: str
    content: str

@app.post("/chat/", response_model=MessageResponse)
async def create_chat(
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    # 简单的对话实现
    response = await llm.get_response([
        {"role": "user", "content": message.content}
    ])
    
    if response is None:
        raise HTTPException(status_code=500, detail="Failed to get response from LLM")
    
    return MessageResponse(role="assistant", content=response)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)