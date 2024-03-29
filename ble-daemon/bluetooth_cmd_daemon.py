from lib.mqtt import MQTTClient
from lib.bluetooth import BLEConn, BLEScanner, BLEDevice
import asyncio
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("bluetooth")

class BluetoothCMDDaemon(object):

    def __init__(self):
        self.mqtt_client = MQTTClient(self.on_mqtt_message)

    def on_mqtt_message(self, topic: str, payload: any):
        topic_attrs = topic.split("/")
        address = topic_attrs[0]
        fn = ""
        if len(topic_attrs) > 1:
            fn = topic_attrs[1]
        if fn == "":
            logger.error("recovered from error - no function provided on mqtt")
            return
        if payload is None or len(payload) < 1:
            logger.error("recovered from error - no command provided on mqtt")
            return
        ble_client = BLEConn(address=address)
        print(payload.decode('ascii'))
        try:
            asyncio.run(ble_client.run_single_ble_command(read_chan=os.environ.get("BLE_READ_CH"), write_chan=os.environ.get("BLE_WRITE_CH"), cmd = payload))
            # self.loop.run_until_complete(ble_client.connect())
        except Exception as e:
            logger.error(f"recovered from ble error - check your command")
            logger.exception(e)
            return

load_dotenv()
main_loop = asyncio.get_event_loop()
daemon = BluetoothCMDDaemon()
main_loop.run_forever()