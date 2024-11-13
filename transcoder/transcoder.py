from gateway.mqtt import MQTTClient
import asyncio
from dotenv import load_dotenv
import os
import logging
from gateway.json_helper import bytes_to_strings
from utils.decoding import Decoder
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - {%(pathname)s:%(lineno)d}')
logger = logging.getLogger("transcoder")
main_loop = asyncio.new_event_loop()
ble_loop = asyncio.new_event_loop()
bg_loop = asyncio.new_event_loop()
decoder = Decoder()
class Transcoder(object):

    def __init__(self):
        self.mqtt_client = MQTTClient(self.on_mqtt_message, name="transcoding_daemon")
        self.address = ""

    def on_mqtt_message(self, topic: str, payload: any):
        topic_attrs = topic.split("/")
        address = topic_attrs[0]
        self.address = address
        key = ""
        if len(topic_attrs) <= 1 or topic_attrs[1] != "advertisements":
            print(topic_attrs)
            return
        if len(topic_attrs) > 2:
            key = topic_attrs[2]
        if key == "":
            logger.error("recovered from error - no function provided on mqtt")
            return
        if payload is None or len(payload) < 1:
            logger.error("recovered from error - no command provided on mqtt")
            return
        print(payload)
        try:
            if key == "manufacturer_data":
                decoded_data = decoder.decode_advertisement(payload)
                logger.info(decoded_data)
                self.mqtt_client.send_message(f"{topic_attrs[0]}/{topic_attrs[1]}/decoded_advertisements", json.dumps(decoded_data))
                logger.info("decoding")
                
            elif key == "encode":
                logger.info("encoding")
            else:
                logger.info(f"nothing to decode on {key}")
            # ble_loop.run_until_complete()
            # self.loop.run_until_complete(ble_client.connect())
        except Exception as e:
            logger.error(f"recovered from decoding error - check your command")
            logger.exception(e)
            return

load_dotenv()
daemon = Transcoder()
main_loop.run_forever()