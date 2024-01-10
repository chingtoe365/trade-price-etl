""" Program wide utilities"""


def build_mqtt_topic(trade_item: str, signal: str):
    """ Build MQTT topic name with trade item and signal

    @param price:
    @param signal:
    @return:
    """
    return f'{trade_item.replace(" ", "-").replace("/", "-").lower()}/{signal}'
