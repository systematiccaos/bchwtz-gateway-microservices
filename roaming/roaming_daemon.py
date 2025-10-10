from gateway.mqtt import MQTTClient
import asyncio
from dotenv import load_dotenv
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - {%(pathname)s:%(lineno)d}')
logger = logging.getLogger("roaming")
logger.setLevel(logging.INFO)
main_loop = asyncio.new_event_loop()
ble_loop = asyncio.new_event_loop()
bg_loop = asyncio.new_event_loop()
class RoamingDaemon(object):

    def __init__(self):
        self.mqtt_client = MQTTClient(self.on_mqtt_message, name="roaming_daemon")
        self.address = ""
        self.strongest_gw = ""
        self.strongest_rssi = 0

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
            if key == "rssi":
                print(f"setting rssi to {payload}")
                gw = topic_attrs[3]
                if self.strongest_gw == "" or self.strongest_rssi < payload:
                    self.mqtt_client.send_message(f"{topic_attrs[0]}/decoded/state/gateway_selection/active/address", gw)
                    self.mqtt_client.send_message(f"{topic_attrs[0]}/decoded/state/gateway_selection/active/rssi", payload)
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
daemon = RoamingDaemon()
main_loop.run_forever()