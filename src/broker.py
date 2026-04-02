from faststream.rabbit import RabbitBroker
from src.common.config import get_settings


broker = RabbitBroker(get_settings().rabbitmq_url)
