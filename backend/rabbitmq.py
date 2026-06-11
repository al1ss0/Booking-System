#Envio de mensagens para RabbitMQ

import json
import aio_pika

rabbitmq_connection = None


async def get_rabbitmq():
    global rabbitmq_connection

    if rabbitmq_connection is None or rabbitmq_connection.is_closed:
        rabbitmq_connection = await aio_pika.connect_robust(
            "amqp://guest:guest@rabbitmq/"
        )

    return rabbitmq_connection


async def publicar_notificacao(mensagem: dict):
    try:
        conn = await get_rabbitmq()
        channel = await conn.channel()

        await channel.declare_queue("notificacoes", durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(mensagem).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key="notificacoes",
        )

    except Exception as e:
        print(f"[RabbitMQ] Erro ao publicar: {e}")


async def fechar_rabbitmq():
    global rabbitmq_connection

    if rabbitmq_connection:
        await rabbitmq_connection.close()