from fastapi import APIRouter
from app.services.store import get_leaderboard

router = APIRouter()

@router.get("/")
def read_leaderboard():
    return {"leaderboard": get_leaderboard()}
