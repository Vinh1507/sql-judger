from dramatiq.brokers.rabbitmq import RabbitmqBroker
import dramatiq

# Set up RabbitMQ broker with a custom queue
rabbitmq_broker = RabbitmqBroker(
    url="amqp://guest:guest@localhost:5673/",
)

# Set the broker for Dramatiq
dramatiq.set_broker(rabbitmq_broker)
