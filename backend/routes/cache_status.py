from fastapi import APIRouter
from cache import redis_client, REDIS_URL

router = APIRouter()


@router.get("/cache/status")
async def cache_status():
    try:
        await redis_client.ping()
        return {
            "redis": "conectado",
            "url": REDIS_URL,
        }

    except Exception as e:
        return {
            "redis": "erro",
            "detalhe": str(e),
        }