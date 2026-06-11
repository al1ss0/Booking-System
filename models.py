#Define as tabelas do PostgreSQL

import databases
import sqlalchemy
from datetime import datetime

DATABASE_URL = "postgresql://admin:admin123@db:5432/reservas"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Tabela de usuários
usuarios = sqlalchemy.Table(
    "usuarios",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("usuario", sqlalchemy.String(50), unique=True, nullable=False),
    sqlalchemy.Column("senha", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("perfil", sqlalchemy.String(20), nullable=False, default="aluno"),
    sqlalchemy.Column("nome", sqlalchemy.String(100), nullable=False),
)

# Tabela de salas
salas = sqlalchemy.Table(
    "salas",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nome", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("capacidade", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("localizacao", sqlalchemy.String(200)),
    sqlalchemy.Column("descricao", sqlalchemy.Text, default=""),
    sqlalchemy.Column("uso_recomendado", sqlalchemy.String(300), default=""),
    sqlalchemy.Column("hora_abertura", sqlalchemy.String(5), default="08:00"),
    sqlalchemy.Column("hora_fechamento", sqlalchemy.String(5), default="23:00"),
)

# Tabela de reservas
reservas = sqlalchemy.Table(
    "reservas",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("sala_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("salas.id"), nullable=False),
    sqlalchemy.Column("usuario", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("data_inicio", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("data_fim", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("status", sqlalchemy.String(20), default="ativa"),
    sqlalchemy.Column("criado_em", sqlalchemy.DateTime, default=datetime.utcnow),
)

SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
engine = sqlalchemy.create_engine(SYNC_DATABASE_URL)