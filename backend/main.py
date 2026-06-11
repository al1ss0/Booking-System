# Inicia FastAPI, conecta ao banco de dados, cria dados iniciais e configura rotas e cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import database, metadata, engine
from seed import criar_dados_iniciais
from backend.cache import (
    redis_client,
    invalidar_cache_salas,
    invalidar_cache_reservas,
    invalidar_cache_usuarios,
)
from rabbitmq import fechar_rabbitmq
from routes import usuarios, salas, reservas, cache_status

metadata.create_all(engine)

app = FastAPI(title="Sistema de Reservas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(salas.router)
app.include_router(reservas.router)
app.include_router(cache_status.router)


@app.on_event("startup")
async def startup():
    await database.connect()

    await criar_dados_iniciais()

    await invalidar_cache_salas()
    await invalidar_cache_reservas()
    await invalidar_cache_usuarios()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await redis_client.close()
    await fechar_rabbitmq()