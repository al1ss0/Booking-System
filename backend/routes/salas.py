from fastapi import APIRouter, HTTPException

from models import database, salas, reservas
from schemas import SalaCreate, SalaUpdate
from cache import (
    cache_get,
    cache_set,
    invalidar_cache_salas,
    invalidar_cache_reservas,
)

router = APIRouter()


@router.get("/salas")
async def listar_salas():
    cache = await cache_get("salas:todas")

    if cache:
        return cache

    resultado = await database.fetch_all(
        salas.select().order_by(salas.c.nome)
    )

    dados = [dict(sala) for sala in resultado]

    await cache_set("salas:todas", dados, tempo=120)

    return dados


@router.get("/salas/{sala_id}")
async def detalhe_sala(sala_id: int):
    chave = f"salas:{sala_id}"

    cache = await cache_get(chave)

    if cache:
        return cache

    sala = await database.fetch_one(
        salas.select().where(salas.c.id == sala_id)
    )

    if not sala:
        raise HTTPException(
            status_code=404,
            detail="Sala não encontrada",
        )

    dados = dict(sala)

    await cache_set(chave, dados, tempo=120)

    return dados


@router.post("/salas", status_code=201)
async def criar_sala(sala: SalaCreate):
    sala_id = await database.execute(
        salas.insert().values(**sala.model_dump())
    )

    await invalidar_cache_salas()

    return {
        "id": sala_id,
        **sala.model_dump(),
    }


@router.patch("/salas/{sala_id}")
async def atualizar_sala(sala_id: int, dados: SalaUpdate):
    sala = await database.fetch_one(
        salas.select().where(salas.c.id == sala_id)
    )

    if not sala:
        raise HTTPException(
            status_code=404,
            detail="Sala não encontrada",
        )

    update_data = {
        chave: valor
        for chave, valor in dados.model_dump().items()
        if valor is not None
    }

    if update_data:
        await database.execute(
            salas
            .update()
            .where(salas.c.id == sala_id)
            .values(**update_data)
        )

    await invalidar_cache_salas()
    await invalidar_cache_reservas()

    return {"mensagem": "Sala atualizada com sucesso"}


@router.delete("/salas/{sala_id}")
async def deletar_sala(sala_id: int):
    sala = await database.fetch_one(
        salas.select().where(salas.c.id == sala_id)
    )

    if not sala:
        raise HTTPException(
            status_code=404,
            detail="Sala não encontrada",
        )

    await database.execute(
        "DELETE FROM reservas WHERE sala_id = :sala_id",
        values={"sala_id": sala_id},
    )

    await database.execute(
        salas.delete().where(salas.c.id == sala_id)
    )

    await invalidar_cache_salas()
    await invalidar_cache_reservas()

    return {"mensagem": "Sala e reservas vinculadas removidas com sucesso"}