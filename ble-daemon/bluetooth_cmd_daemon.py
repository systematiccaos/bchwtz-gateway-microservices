import time
from daemon.mqtt import MQTTClient
from daemon.bluetooth import BLEConn, BLEScanner, BLEDevice
import asyncio
from dotenv import load_dotenv
import os
import logging
from daemon.json_helper import bytes_to_strings

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("bluetooth")

class BluetoothCMDDaemon(object):

    def __init__(self):
        self.mqtt_client = MQTTClient(self.on_mqtt_message, name="cmd_daemon")
        self.address = ""
        self.mqtt_client.send_message(f"log", msg = "online")


    def on_ble_response(self, status: int, response: bytearray):
        res = bytes_to_strings(response)
        logger.info(res)
        self.mqtt_client.send_message(f"{self.address}/response", msg = str(res))


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
        print(payload.decode('ascii'))
        try:
            if fn == "run_single_ble_command":
                logger.info("running command")
                asyncio.run(ble_client.run_single_ble_command(read_chan=os.environ.get("BLE_READ_CH"), write_chan=os.environ.get("BLE_WRITE_CH"), cmd = payload, cb=self.on_ble_response))
            else:
                logger.error(f"function not available")
            # self.loop.run_until_complete(ble_client.connect())
        except Exception as e:
            logger.error(f"recovered from ble error - check your command")
            logger.exception(e)
            return

load_dotenv()
daemon = BluetoothCMDDaemon()
asyncio.get_event_loop().run_forever()