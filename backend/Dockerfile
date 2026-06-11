# Imagem base do Python
FROM python:3.11-slim

# Evita gerar arquivos .pyc e melhora logs no Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia apenas as dependências primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Instala as dependências do backend
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do backend para o container
COPY . .

# Expõe a porta usada pela API FastAPI
EXPOSE 8000

# Comando padrão para iniciar o backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]