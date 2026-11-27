"""WebSocket endpoint for real-time telemetry streaming and simulation updates."""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(prefix="/ws", tags=["Real-Time WebSockets"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/live-feed")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial confirmation
        await websocket.send_text(json.dumps({
            "event": "CONNECTED",
            "message": "Connected to AI Disaster Response live telemetry stream."
        }))
        while True:
            data = await websocket.receive_text()
            # Echo or process client command
            await websocket.send_text(json.dumps({
                "event": "ACK",
                "received": data
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
