FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Arquivo que prepara o ambiente do servidor. Ele usa Python 3.11, instala as dependências do projeto pelo requirements.txt, copia o código da aplicação e inicia a API FastAPI com Uvicorn na porta 8000. 
# Ele que garante que o backend rode de forma padronizada dentro de um container Docker.