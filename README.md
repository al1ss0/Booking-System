# 🎓 Booking System

> Sistema distribuído de reservas de laboratórios, salas de reunião e auditórios da ATITUS Educação.

O **Booking System** é uma aplicação que permite que professores reservem laboratórios e salas da faculdade de forma simples e organizada. O sistema controla conflitos de horário automaticamente, exibe apenas os slots disponíveis e notifica via fila de mensagens a cada reserva realizada.

---

### 🛠️ Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| API REST | Python + FastAPI |
| Banco de dados | PostgreSQL |
| Cache distribuído | Redis |
| Mensageria | RabbitMQ |
| Frontend | HTML + CSS + JavaScript |
| Infraestrutura | Docker  |


### 🏗️ Arquitetura

```
Frontend (HTML/CSS/JS)
        │
        ▼
   FastAPI (API REST)
   ├── Redis       → cache distribuído (salas, reservas, usuários)
   └── RabbitMQ    → fila de notificações
                          │
                          ▼
                       Worker
                  (consome a fila e
                  processa notificações)

```
---

### 🚀 Como Rodar

### Pré-requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando

### 1. Clona o repositório

```bash
git clone https://github.com/al1ss0/Booking-System.git
cd Booking-System
```

### 2. Suba todos os serviços

```bash
docker compose up --build
```

Na primeira execução, aguarde o download das imagens.

### 3. Acesse o sistema


| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Sistema | http://localhost:3000 | — |
| API (docs) | http://localhost:8000/docs | — |
| RabbitMQ | http://localhost:15672 | guest / guest |
| PgAdmin | http://localhost:5050 | admin@admin.com / admin123 |

### Usuários padrão do sistema

| Usuário | Senha | Perfil |
|---------|-------|--------|
| admin | admin123 | Administrador |
| alisson | prof123 | Professor |



---

### 📡 Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/login` | Autenticação |
| GET | `/salas` | Lista todas as salas |
| POST | `/salas` | Cria nova sala |
| PATCH | `/salas/{id}` | Edita sala |
| DELETE | `/salas/{id}` | Remove sala |
| GET | `/reservas` | Lista todas as reservas |
| GET | `/reservas/usuario/{usuario}` | Reservas de um aluno |
| GET | `/reservas/slots/{sala_id}` | Slots disponíveis por data |
| POST | `/reservas` | Cria reserva |
| DELETE | `/reservas/{id}` | Cancela reserva |
| POST | `/reservas/expirar` | Marca reservas passadas como concluídas |
| GET | `/professores` | Lista professores cadastrados |
| POST | `/professores` | Cadastra novo professor |
| DELETE | `/professores/{usuario}` | Remove professor |

---

### 🐳 Serviços Docker

```yaml
reservas_api      → FastAPI na porta 8000
reservas_worker   → Consumidor RabbitMQ
reservas_db       → PostgreSQL na porta 5432
reservas_rabbitmq → RabbitMQ nas portas 5672 / 15672
reservas_pgadmin  → PgAdmin na porta 5050
```

Para acompanhar as notificações do Worker em tempo real:

```bash
docker logs -f reservas_worker
```

