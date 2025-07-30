import paho.mqtt.client as mqtt
from ..configuration.core_configuration import MQTTConfig
import json
import logging as log


def publish_message(config: MQTTConfig, topic: str, message: dict) -> None:
    """
    Publishes a message to an MQTT broker.

    Args:
        config (MQTTConfig): The MQTT configuration object.
        topic (str): The topic to publish the message to.
        message (str): The message to be published.

    Returns:
        None
    """
    if config.enabled:
        client = mqtt.Client()
        client.connect(config.host, 1883, 60)
        client.publish(topic, str(json.dumps(message)))
        client.disconnect()
        log.debug("published message to %s", topic)
