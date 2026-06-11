#Funções do Redis

import os
import json
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


async def cache_get(chave: str):
    try:
        valor = await redis_client.get(chave)

        if valor:
            print(f"[Redis] HIT: {chave}")
            return json.loads(valor)

        print(f"[Redis] MISS: {chave}")
        return None

    except Exception as e:
        print(f"[Redis] Erro ao buscar cache: {e}")
        return None


async def cache_set(chave: str, valor, tempo: int = 60):
    try:
        await redis_client.set(
            chave,
            json.dumps(valor, default=str),
            ex=tempo
        )

        print(f"[Redis] SET: {chave}")

    except Exception as e:
        print(f"[Redis] Erro ao salvar cache: {e}")


async def cache_delete_pattern(pattern: str):
    try:
        async for chave in redis_client.scan_iter(pattern):
            await redis_client.delete(chave)
            print(f"[Redis] DEL: {chave}")

    except Exception as e:
        print(f"[Redis] Erro ao limpar cache: {e}")


async def invalidar_cache_salas():
    await cache_delete_pattern("salas:*")


async def invalidar_cache_reservas():
    await cache_delete_pattern("reservas:*")


async def invalidar_cache_usuarios():
    await cache_delete_pattern("usuarios:*")