from dramatiq.brokers.rabbitmq import RabbitmqBroker
import dramatiq

# Set up RabbitMQ broker with a custom queue
rabbitmq_broker = RabbitmqBroker(
    url="amqp://guest:guest@localhost:5672/",
    # options={"queue_name": "letterbox"}
)

# Set the broker for Dramatiq
dramatiq.set_broker(rabbitmq_broker)
