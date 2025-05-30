import os
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio

# 挂载静态文件目录
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'static', 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

app = FastAPI()
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# 挂载前端静态文件目录
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend")

# 导入对话机器人核心逻辑
from agents.chat_agent import ChatAgent
chat_agent = ChatAgent(model_type="tongyi")

# WebSocket 聊天接口
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    session_id = None
    interrupted = False
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")
            session_id = data.get("session_id") or str(uuid.uuid4())
            if interrupted:
                print(f"[WS] 收到 resume_chat: {message}, session_id={session_id}")
                async for chunk in chat_agent.resume_chat(message, session_id, websocket=websocket):
                    print(f"[WS] resume_chat yield: {chunk}")
                    await websocket.send_json(chunk)
                interrupted = False
            else:
                print(f"[WS] chat: {message}, session_id={session_id}")
                async for chunk in chat_agent.chat(message, session_id, websocket=websocket):
                    print(f"[WS] chat yield: {chunk}")
                    await websocket.send_json(chunk)
                    if chunk.get("type") == "interrupt":
                        interrupted = True
    except WebSocketDisconnect:
        print(f"Session {session_id} disconnected")

@app.get("/")
async def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    print("启动服务器，请访问以下地址：")
    # 使用0.0.0.0而不是127.0.0.1使服务器在网络上可访问
    uvicorn.run(app, host="0.0.0.0", port=8000)