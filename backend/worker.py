#Consome mensagens do RabbitMQ

import asyncio
import aio_pika
import json
from datetime import datetime

async def processar_mensagem(message: aio_pika.IncomingMessage):
    async with message.process():
        dados = json.loads(message.body.decode())
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        tipo = dados.get("tipo")

        if tipo == "RESERVA_CRIADA":
            print(f"\n{'='*50}")
            print(f"[{agora}] 📬 NOVA NOTIFICAÇÃO — RESERVA CRIADA")
            print(f"  Reserva ID : #{dados['reserva_id']}")
            print(f"  Usuário    : {dados['usuario']}")
            print(f"  Sala       : {dados['sala']}")
            print(f"  Início     : {dados['data_inicio']}")
            print(f"  Fim        : {dados['data_fim']}")
            print(f"  [OK] Notificação processada — e-mail seria enviado aqui")
            print(f"{'='*50}\n")

        elif tipo == "RESERVA_CANCELADA":
            print(f"\n{'='*50}")
            print(f"[{agora}] ❌ NOVA NOTIFICAÇÃO — RESERVA CANCELADA")
            print(f"  Reserva ID : #{dados['reserva_id']}")
            print(f"  Usuário    : {dados['usuario']}")
            print(f"  Sala       : {dados['sala']}")
            print(f"  [OK] Notificação processada — e-mail seria enviado aqui")
            print(f"{'='*50}\n")

        else:
            print(f"[{agora}] Mensagem desconhecida: {dados}")

async def main():
    print("🐇 Worker RabbitMQ iniciado — aguardando mensagens...")
    
    # Tenta conectar, aguarda o RabbitMQ subir
    while True:
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
            break
        except Exception:
            print("Aguardando RabbitMQ...")
            await asyncio.sleep(3)

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue("notificacoes", durable=True)
    await queue.consume(processar_mensagem)

    print("✅ Worker conectado e ouvindo a fila 'notificacoes'")
    await asyncio.Future()  # roda para sempre

if _name_ == "_main_":
    asyncio.run(main())