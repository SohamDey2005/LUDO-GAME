from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.sockets.manager import manager
from app.services.store import get_game

router = APIRouter()

@router.websocket("/ws/game/{game_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, client_id: str):
    await manager.connect(websocket, game_id)
    try:
        # Immediately send current state upon connection
        game = get_game(game_id)
        await websocket.send_json({"type": "STATE_UPDATE", "data": game.model_dump(mode='json')})
        
        while True:
            # We can accept incoming websocket messages here if needed
            # For now, all game actions are done via REST, and WebSockets are for reading state syncs
            data = await websocket.receive_text()
            pass
    except ValueError:
        await websocket.close(code=1008, reason="Game not found")
    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
