from fastapi import APIRouter, HTTPException
from datetime import datetime, date as date_type

from models import database, salas, reservas, usuarios
from schemas import ReservaCreate
from cache import cache_get, cache_set, invalidar_cache_reservas
from rabbitmq import publicar_notificacao

router = APIRouter()


@router.post("/reservas/expirar")
async def expirar_reservas():
    await database.execute(
        """UPDATE reservas SET status = 'concluida'
           WHERE status = 'ativa' AND data_fim < NOW()"""
    )

    await invalidar_cache_reservas()

    return {"mensagem": "Reservas expiradas atualizadas"}


@router.get("/reservas")
async def listar_reservas():
    cache = await cache_get("reservas:todas")

    if cache:
        return cache

    query = """
        SELECT r.id, r.usuario, r.data_inicio, r.data_fim, r.status, r.criado_em,
               s.nome as sala_nome, s.localizacao
        FROM reservas r
        JOIN salas s ON s.id = r.sala_id
        ORDER BY r.data_inicio DESC
    """

    resultado = await database.fetch_all(query)
    dados = [dict(reserva) for reserva in resultado]

    await cache_set("reservas:todas", dados, tempo=60)

    return dados


@router.get("/reservas/usuario/{usuario}")
async def reservas_por_usuario(usuario: str):
    chave = f"reservas:usuario:{usuario}"

    cache = await cache_get(chave)

    if cache:
        return cache

    query = """
        SELECT r.id, r.usuario, r.data_inicio, r.data_fim, r.status, r.criado_em,
               s.nome as sala_nome, s.localizacao
        FROM reservas r
        JOIN salas s ON s.id = r.sala_id
        WHERE r.usuario = :usuario
        ORDER BY r.data_inicio DESC
    """

    resultado = await database.fetch_all(
        query,
        values={"usuario": usuario},
    )

    dados = [dict(reserva) for reserva in resultado]

    await cache_set(chave, dados, tempo=60)

    return dados


@router.get("/reservas/slots/{sala_id}")
async def slots_disponiveis(sala_id: int, data: str):
    chave = f"reservas:slots:{sala_id}:{data}"

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

    hoje = datetime.now().date()
    data_obj = date_type.fromisoformat(data)

    if data_obj < hoje:
        return []

    abertura = int(sala["hora_abertura"].split(":")[0])
    fechamento = int(sala["hora_fechamento"].split(":")[0])

    todos_slots = []

    for hora in range(abertura, fechamento):
        inicio = f"{data}T{hora:02d}:00:00"
        fim = f"{data}T{hora + 1:02d}:00:00"

        todos_slots.append({
            "inicio": inicio,
            "fim": fim,
            "label": f"{hora:02d}:00 – {hora + 1:02d}:00",
        })

    reservas_dia = await database.fetch_all(
        """SELECT data_inicio, data_fim FROM reservas
           WHERE sala_id = :sala_id
             AND status = 'ativa'
             AND DATE(data_inicio) = :data""",
        values={
            "sala_id": sala_id,
            "data": data_obj,
        },
    )

    agora = datetime.now()
    slots = []

    for slot in todos_slots:
        ocupado = False
        slot_inicio = datetime.fromisoformat(slot["inicio"])

        if slot_inicio <= agora:
            ocupado = True

        for reserva in reservas_dia:
            reserva_inicio = reserva["data_inicio"].strftime("%H:%M")
            reserva_fim = reserva["data_fim"].strftime("%H:%M")
            slot_inicio_hora = slot["label"].split(" – ")[0]
            slot_fim_hora = slot["label"].split(" – ")[1]

            if not (
                slot_fim_hora <= reserva_inicio
                or slot_inicio_hora >= reserva_fim
            ):
                ocupado = True
                break

        slots.append({
            **slot,
            "disponivel": not ocupado,
        })

    await cache_set(chave, slots, tempo=30)

    return slots


@router.post("/reservas", status_code=201)
async def criar_reserva(reserva: ReservaCreate):
    agora = datetime.now()

    if reserva.data_inicio < agora:
        raise HTTPException(
            status_code=400,
            detail="Não é possível reservar datas ou horários que já passaram",
        )

    if reserva.data_fim <= reserva.data_inicio:
        raise HTTPException(
            status_code=400,
            detail="Horário inválido",
        )

    sala = await database.fetch_one(
        salas.select().where(salas.c.id == reserva.sala_id)
    )

    if not sala:
        raise HTTPException(
            status_code=404,
            detail="Sala não encontrada",
        )

    user = await database.fetch_one(
        usuarios.select().where(usuarios.c.usuario == reserva.usuario)
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado",
        )

    hora_inicio = reserva.data_inicio.strftime("%H:%M")
    hora_fim = reserva.data_fim.strftime("%H:%M")

    if hora_inicio < sala["hora_abertura"] or hora_fim > sala["hora_fechamento"]:
        raise HTTPException(
            status_code=400,
            detail=f"Esta sala funciona das {sala['hora_abertura']} às {sala['hora_fechamento']}",
        )

    conflito = await database.fetch_one(
        """SELECT id FROM reservas
           WHERE sala_id = :sala_id
             AND status = 'ativa'
             AND NOT (:data_fim <= data_inicio OR :data_inicio >= data_fim)""",
        values={
            "sala_id": reserva.sala_id,
            "data_inicio": reserva.data_inicio,
            "data_fim": reserva.data_fim,
        },
    )

    if conflito:
        raise HTTPException(
            status_code=409,
            detail="Sala já reservada neste horário",
        )

    reserva_id = await database.execute(
        reservas.insert().values(
            sala_id=reserva.sala_id,
            usuario=reserva.usuario,
            data_inicio=reserva.data_inicio,
            data_fim=reserva.data_fim,
            status="ativa",
            criado_em=datetime.utcnow(),
        )
    )

    await publicar_notificacao({
        "tipo": "RESERVA_CRIADA",
        "reserva_id": reserva_id,
        "usuario": reserva.usuario,
        "sala": sala["nome"],
        "data_inicio": reserva.data_inicio.isoformat(),
        "data_fim": reserva.data_fim.isoformat(),
    })

    await invalidar_cache_reservas()

    return {
        "id": reserva_id,
        "mensagem": "Reserva criada com sucesso!",
    }


@router.delete("/reservas/{reserva_id}")
async def cancelar_reserva(reserva_id: int):
    reserva = await database.fetch_one(
        reservas.select().where(reservas.c.id == reserva_id)
    )

    if not reserva:
        raise HTTPException(
            status_code=404,
            detail="Reserva não encontrada",
        )

    if reserva["status"] == "cancelada":
        raise HTTPException(
            status_code=400,
            detail="Reserva já cancelada",
        )

    await database.execute(
        reservas
        .update()
        .where(reservas.c.id == reserva_id)
        .values(status="cancelada")
    )

    sala = await database.fetch_one(
        salas.select().where(salas.c.id == reserva["sala_id"])
    )

    await publicar_notificacao({
        "tipo": "RESERVA_CANCELADA",
        "reserva_id": reserva_id,
        "usuario": reserva["usuario"],
        "sala": sala["nome"],
    })

    await invalidar_cache_reservas()

    return {"mensagem": "Reserva cancelada com sucesso!"}