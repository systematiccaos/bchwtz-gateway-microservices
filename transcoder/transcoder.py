from gateway.mqtt import MQTTClient
import asyncio
from dotenv import load_dotenv
import logging
from utils.decoding import Decoder
from utils.signals import SigScanner
import json
from gateway.config import Config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - {%(pathname)s:%(lineno)d}')
logger = logging.getLogger("transcoder")
logger.setLevel(logging.INFO)
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
        payloadstr = payload.decode('utf-8')
        if payloadstr == 'error':
            logger.info('error')
            return
        if len(topic_attrs) < 2:
            return
        if topic_attrs[1] == "response" and payloadstr != "":
            logger.info(payloadstr)
            logger.info("decoding sig")
            sig = SigScanner.scan_signals(bytearray.fromhex(payloadstr), Config.ReturnSignals)
            logger.info(sig)
            if sig is None:
                return
            if "config" in sig:
                decoded_data = decoder.decode_config_rx(bytearray.fromhex(payloadstr))
                # self.mqtt_client.send_message(f"{topic_attrs[0]}/decoded/config", json.dumps(decoded_data.get_props()))
                self.log_object_as_vals(f"{topic_attrs[0]}/decoded/config", decoded_data.get_props())
                return
            if "time" in sig:
                decoded_data = decoder.decode_time_rx(bytearray.fromhex(payloadstr))
                self.mqtt_client.send_message(f"{topic_attrs[0]}/decoded/time", decoded_data)
                return
            if "heartbeat" in sig:
                decoded_data = decoder.decode_heartbeat_rx(bytearray.fromhex(payloadstr))
                self.mqtt_client.send_message(f"{topic_attrs[0]}/decoded/heartbeat", decoded_data)
                return
            return
        elif topic_attrs[1] == "stream":
            logger.info(payloadstr)
            try:
                data8, data10, data12 = decoder.decode_acc_stream_pack(bytearray.fromhex(payloadstr))
                [self.log_object_as_vals(f"{topic_attrs[0]}/decoded/stream/data8", d) for d in data8]
                [self.log_object_as_vals(f"{topic_attrs[0]}/decoded/stream/data10", d) for d in data10]
                [self.log_object_as_vals(f"{topic_attrs[0]}/decoded/stream/data12", d) for d in data12]
            except Exception as e:
                logger.error(e)

        elif topic_attrs[1] != "advertisements":
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

            if key == "manufacturer_data" and payload is not None:
                decoded_data = decoder.decode_advertisement(payload)
                logger.info(decoded_data)
                # self.mqtt_client.send_message(f"{topic_attrs[0]}/decoded/advertisements", json.dumps(decoded_data))
                self.log_object_as_vals(f"{topic_attrs[0]}/decoded/advertisements", decoded_data=decoded_data)
                logger.info("decoding")
            if key == "rssi":
                print(f"setting rssi to {payload}")
                self.mqtt_client.send_message(f"{topic_attrs[0]}/decoded/gateway/rssi/{topic_attrs[3]}", payload)
            if key == "name":
                print(f"setting name to {payload}")
                self.mqtt_client.send_message(f"{topic_attrs[0]}/decoded/name", payload)
            else:
                logger.info(f"nothing to decode on {key}")
            # ble_loop.run_until_complete()
            # self.loop.run_until_complete(ble_client.connect())
        except Exception as e:
            logger.error(f"recovered from decoding error - check your command")
            logger.exception(e)
            return
    def log_object_as_vals(self, chan, decoded_data):
        for key, val in decoded_data.items():
            self.mqtt_client.send_message(f"{chan}/{key}", val)

load_dotenv()
daemon = Transcoder()
main_loop.run_forever()