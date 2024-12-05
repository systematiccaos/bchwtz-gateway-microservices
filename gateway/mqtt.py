import paho.mqtt.client as mqtt
import os
import re
import uuid
import logging

logger = logging.getLogger()

class MQTTClient():
    def __init__(self, callback: callable, name: str, asnc: bool = True, nostart = False) -> None:
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION1,
            client_id = os.environ.get("MQTT_CLIENT_ID", "default_client") + "_" + name + str(uuid.uuid4()),
            clean_session = True,
            userdata = None,
            transport = 'tcp',
        )
        self.root_topic_raw: str = os.environ.get("MQTT_ROOT_TOPIC", "")
        self.root_topic = "#" if self.root_topic_raw == "" else f"{self.root_topic_raw}/#"
        self.client.on_message = self.consume_message
        self.cb = callback
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(
            username = os.environ.get("MQTT_USER", "mqtt"),
            password = os.environ.get("MQTT_PASSWORD", "changeme"),
        )
        self.client.connect(
            host = os.environ.get("MQTT_HOST", "localhost"),
            port = int(os.environ.get("MQTT_PORT", 1883)),
        )
        if asnc:
            self.client.loop_start()
        elif not nostart:
            self.client.loop_forever()
        else:
            logger.info("no startup")

    def send_message(self, topic: str, msg: any):
        self.client.publish(self.root_topic_raw + "/" + topic, msg)

    def consume_message(self, client: mqtt.Client, userdata: dict, msg: mqtt.MQTTMessage):
        pattern = re.compile(r'^' + re.escape(self.root_topic_raw) + r'(\/)?')
        topic = pattern.sub('', msg.topic)
        logger.debug(self.root_topic_raw)
        self.cb(topic, msg.payload)

    def on_connect(self, client, userdata, flags, reason_code):
        print(f"Connected to mqtt with result code {reason_code}")
        client.subscribe(f"{self.root_topic}")

    def on_disconnect(self, client: mqtt, userdata, flags):
        print("disconnected")