from fastapi import APIRouter, HTTPException

from models import database, usuarios
from schemas import LoginRequest, AlunoCadastro
from cache import cache_get, cache_set, invalidar_cache_usuarios

router = APIRouter()


@router.post("/alunos", status_code=201)
async def cadastrar_aluno(req: AlunoCadastro):
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
            perfil="aluno",
            nome=nome,
        )
    )

    await invalidar_cache_usuarios()

    return {"mensagem": f"Aluno {nome} cadastrado com sucesso"}


@router.delete("/alunos/{usuario}")
async def excluir_aluno(usuario: str):
    aluno = await database.fetch_one(
        usuarios.select().where(usuarios.c.usuario == usuario)
    )

    if not aluno:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado",
        )

    if aluno["perfil"] == "admin":
        raise HTTPException(
            status_code=403,
            detail="Não é possível excluir o admin",
        )

    await database.execute(
        usuarios.delete().where(usuarios.c.usuario == usuario)
    )

    await invalidar_cache_usuarios()

    return {"mensagem": f"Aluno {usuario} excluído com sucesso"}


@router.get("/alunos")
async def listar_alunos():
    cache = await cache_get("usuarios:alunos")

    if cache:
        return cache

    resultado = await database.fetch_all(
        usuarios
        .select()
        .where(usuarios.c.perfil == "aluno")
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

    await cache_set("usuarios:alunos", dados, tempo=120)

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