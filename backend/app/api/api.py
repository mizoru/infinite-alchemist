from fastapi import APIRouter
from app.api.endpoints import elements, players, discoveries, prompts

api_router = APIRouter()
api_router.include_router(elements.router, prefix="/elements", tags=["elements"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(discoveries.router, prefix="/discoveries", tags=["discoveries"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"]) 