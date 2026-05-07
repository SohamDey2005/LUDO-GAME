from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as game_router

app = FastAPI(title="Ludo AI Game API", version="1.0.0")

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.websockets import router as ws_router
from app.api.leaderboard import router as leader_router

app.include_router(game_router, prefix="/api/game", tags=["game"])
app.include_router(ws_router, tags=["websockets"])
app.include_router(leader_router, prefix="/api/leaderboard", tags=["leaderboard"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
