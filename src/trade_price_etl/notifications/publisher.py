import logging
import random
import time
import sys

# pip3 install paho-mqtt
from paho.mqtt import client as mqtt_client

from trade_price_etl.settings.base_settings import settings

# broker = 'host.docker.internal'
# port = 1883
logger = logging.getLogger(__name__)

# Generate a Client ID with the publish prefix.
# username = 'admin'
# password = 'password'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
        else:
            logger.error("Failed to connect, return code %d\n", rc)

    logger.debug(f">> before connection")
    client_id = f'publish-{random.randint(0, 1000)}'
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(settings.MQTT_HOST, settings.MQTT_PORT)
    logger.debug(f">> After connection")
    return client


def publish(client, topic, message):
    msg = f"{message}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        logger.info(f"Send `{msg}` to topic `{topic}`")
    else:
        logger.error(f"Failed to send message to topic {topic}")


def publich_message(topic, message):
    client = connect_mqtt()
    client.loop_start()
    publish(client, topic, message)
    client.loop_stop()


MQTT_CLIENT = connect_mqtt()
MQTT_CLIENT.loop_start()


if __name__ == '__main__':
    topic = sys.argv[1]
    message = sys.argv[2]
    publich_message(topic, message)
