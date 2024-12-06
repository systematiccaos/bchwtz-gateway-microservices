from gateway.mqtt import MQTTClient
from bluetooth import BLEConn
import asyncio
from dotenv import load_dotenv
import os
import uuid
import logging
from gateway.json_helper import bytes_to_strings

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - {%(pathname)s:%(lineno)d}')
logger = logging.getLogger("bluetooth")
logger.setLevel(logging.INFO)
main_loop = asyncio.new_event_loop()
ble_loop = asyncio.new_event_loop()
bg_loop = asyncio.new_event_loop()
class BluetoothCMDDaemon(object):

    def __init__(self):
        self.mqtt_client = MQTTClient(self.on_mqtt_message, name="cmd_daemon")
        self.address = ""
        self.mqtt_client.send_message(f"log", msg = "online")
        self.uuid = str(uuid.uuid4())


    def on_ble_response(self, status: int, response: bytearray):
        res = bytes_to_strings(response)
        logger.info(res)
        self.mqtt_client.send_message(f"{self.address}/response/{self.uuid}", msg = res)

    def on_stream_data(self, status: int, response: bytearray):
        res = bytes_to_strings(response)
        logger.info(res)
        res = res[1:]
        self.mqtt_client.send_message(f"{self.address}/stream", msg = res)


    def on_mqtt_message(self, topic: str, payload: any):
        topic_attrs = topic.split("/")
        address = topic_attrs[0]
        self.address = address
        fn = ""
        if len(topic_attrs) <= 1 or (len(topic_attrs) > 1 and topic_attrs[1] != "command"):
            return
        if len(topic_attrs) > 2:
            fn = topic_attrs[2]
        if fn == "":
            logger.error("recovered from error - no function provided on mqtt")
            return
        if payload is None or len(payload) < 1:
            logger.error("recovered from error - no command provided on mqtt")
            return
        ble_client = BLEConn(address=address)
        logger.debug(payload)
        try:
            if fn == "run_single_ble_command":
                logger.info("running command")
                logger.info(payload)
                ble_loop.run_until_complete(ble_client.run_single_ble_command(read_chan=os.environ.get("BLE_READ_CH"), write_chan=os.environ.get("BLE_WRITE_CH"), cmd = payload, cb=self.on_ble_response, await_response=True))
            elif fn == "start_stream":
                ble_loop.run_until_complete(ble_client.run_single_ble_command(read_chan=os.environ.get("BLE_READ_CH"), write_chan=os.environ.get("BLE_WRITE_CH"), cmd = payload, cb=self.on_stream_data, await_response=False))
            elif fn == "stop_stream":
                bg_loop.run_until_complete(ble_client.stopEvent.set())
            else:
                logger.debug(f"function not available for {fn}")
            # ble_loop.run_until_complete()
            # self.loop.run_until_complete(ble_client.connect())
        except Exception as e:
            logger.error(f"recovered from ble error - check your command")
            logger.exception(e)
            self.mqtt_client.send_message("%s/response/error/%s" % (address, self.uuid), "error")
            return

load_dotenv()
daemon = BluetoothCMDDaemon()
main_loop.run_forever()