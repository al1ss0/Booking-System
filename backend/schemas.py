#Define os modelos de entrada para a API

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LoginRequest(BaseModel):
    usuario: str
    senha: str


class AlunoCadastro(BaseModel):
    usuario: str
    senha: str
    nome: Optional[str] = None


class SalaCreate(BaseModel):
    nome: str
    capacidade: int
    localizacao: Optional[str] = None
    descricao: Optional[str] = ""
    uso_recomendado: Optional[str] = ""
    hora_abertura: Optional[str] = "08:00"
    hora_fechamento: Optional[str] = "23:00"


class SalaUpdate(BaseModel):
    nome: Optional[str] = None
    capacidade: Optional[int] = None
    localizacao: Optional[str] = None
    descricao: Optional[str] = None
    uso_recomendado: Optional[str] = None
    hora_abertura: Optional[str] = None
    hora_fechamento: Optional[str] = None


class ReservaCreate(BaseModel):
    sala_id: int
    usuario: str
    data_inicio: datetime
    data_fim: datetime