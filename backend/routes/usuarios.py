from fastapi import APIRouter, HTTPException

from models import database, usuarios
from schemas import LoginRequest, ProfessorCadastro
from cache import cache_get, cache_set, invalidar_cache_usuarios

router = APIRouter()


@router.post("/professores", status_code=201)
async def cadastrar_professor(req: ProfessorCadastro):
    if not req.usuario.strip() or not req.senha.strip():
        raise HTTPException(
            status_code=400,
            detail="Usuário e senha não podem ser vazios",
        )

    existente = await database.fetch_one(
        usuarios.select().where(usuarios.c.usuario == req.usuario)
    )

    if existente:
        raise HTTPException(
            status_code=409,
            detail="Usuário já existe",
        )

    nome = req.nome if req.nome else req.usuario.capitalize()

    await database.execute(
        usuarios.insert().values(
            usuario=req.usuario,
            senha=req.senha,
            perfil="professor",
            nome=nome,
        )
    )

    await invalidar_cache_usuarios()

    return {"mensagem": f"Professor {nome} cadastrado com sucesso"}


@router.delete("/professores/{usuario}")
async def excluir_professor(usuario: str):
    professor = await database.fetch_one(
        usuarios.select().where(usuarios.c.usuario == usuario)
    )

    if not professor:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado",
        )

    if professor["perfil"] == "admin":
        raise HTTPException(
            status_code=403,
            detail="Não é possível excluir o admin",
        )

    await database.execute(
        usuarios.delete().where(usuarios.c.usuario == usuario)
    )

    await invalidar_cache_usuarios()

    return {"mensagem": f"Professor {usuario} excluído com sucesso"}


@router.get("/professores")
async def listar_professores():
    cache = await cache_get("usuarios:professores")

    if cache:
        return cache

    resultado = await database.fetch_all(
        usuarios
        .select()
        .where(usuarios.c.perfil == "professor")
        .order_by(usuarios.c.nome)
    )

    dados = [
        {
            "usuario": u["usuario"],
            "nome": u["nome"],
            "perfil": u["perfil"],
        }
        for u in resultado
    ]

    await cache_set("usuarios:professores", dados, tempo=120)

    return dados


@router.post("/login")
async def login(req: LoginRequest):
    user = await database.fetch_one(
        usuarios.select().where(usuarios.c.usuario == req.usuario)
    )

    if not user or user["senha"] != req.senha:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
        )

    return {
        "usuario": user["usuario"],
        "nome": user["nome"],
        "perfil": user["perfil"],
    }