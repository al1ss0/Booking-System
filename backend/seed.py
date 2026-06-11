#Dados iniciais

from models import database, salas, usuarios

USUARIOS_INICIAIS = [
    {
        "usuario": "admin",
        "senha": "admin123",
        "perfil": "admin",
        "nome": "Administrador",
    },
    {
        "usuario": "alisson",
        "senha": "prof123",
        "perfil": "professor",
        "nome": "Alisson Bosa",
    },
]

SALAS_INICIAIS = [
    {
        "nome": "Auditório",
        "capacidade": 100,
        "localizacao": "Bloco C",
        "descricao": "Espaço amplo com palco, sistema de som e projetor de alta resolução. Ideal para grandes eventos acadêmicos.",
        "uso_recomendado": "Palestras, defesas de TCC, eventos institucionais e apresentações para turmas grandes.",
        "hora_abertura": "08:00",
        "hora_fechamento": "23:00",
    },
]


async def criar_dados_iniciais():
    alter_queries = [
        "ALTER TABLE salas ADD COLUMN IF NOT EXISTS descricao TEXT DEFAULT ''",
        "ALTER TABLE salas ADD COLUMN IF NOT EXISTS uso_recomendado VARCHAR(300) DEFAULT ''",
        "ALTER TABLE salas ADD COLUMN IF NOT EXISTS hora_abertura VARCHAR(5) DEFAULT '08:00'",
        "ALTER TABLE salas ADD COLUMN IF NOT EXISTS hora_fechamento VARCHAR(5) DEFAULT '23:00'",
    ]

    for query in alter_queries:
        try:
            await database.execute(query)
        except Exception:
            pass

    count_usuarios = await database.fetch_val("SELECT COUNT(*) FROM usuarios")

    if count_usuarios == 0:
        await database.execute_many(
            query=usuarios.insert(),
            values=USUARIOS_INICIAIS,
        )

    count_salas = await database.fetch_val("SELECT COUNT(*) FROM salas")

    if count_salas == 0:
        await database.execute_many(
            query=salas.insert(),
            values=SALAS_INICIAIS,
        )