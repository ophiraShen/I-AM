import websockets
import asyncio
import json

async def main():
    uri = "ws://localhost:8657/ws/chat"
    session_id = "affirmtest001"
    async with websockets.connect(uri) as websocket:
        # 1. 发送初始消息，请求生成肯定语
        await websocket.send(json.dumps({"message": "我最近很焦虑，帮我生成一个冥想音频", "session_id": session_id}))
        interrupted = False
        while True:
            try:
                msg = await websocket.recv()
                try:
                    data = json.loads(msg)
                except Exception:
                    print(f"[原始消息] {msg}")
                    continue
                if isinstance(data, dict) and data.get("type") == "progress":
                    print(f"[进度] {data.get('stage')}")
                elif isinstance(data, dict) and data.get("type") == "affirmation":
                    print(f"[肯定语] {data.get('content')}")
                elif isinstance(data, dict) and data.get("type") == "audio":
                    print(f"[音频] {data.get('url')}")
                elif isinstance(data, dict) and data.get("type") == "interrupt":
                    print(f"[中断] {data}")
                    # 自动发送 yes 继续流程
                    if not interrupted:
                        await websocket.send(json.dumps({"message": "yes", "session_id": session_id}))
                        interrupted = True
                elif isinstance(data, dict) and data.get("type") == "message":
                    print(f"[消息] {data.get('content')}")
                else:
                    print(f"[未知] {data}")
            except websockets.ConnectionClosed:
                print("[WebSocket 已关闭]")
                break

asyncio.run(main())