from gateway.mqtt import MQTTClient
from bluetooth import BLEScanner
from gateway.json_helper import bytes_to_strings
import asyncio
from dotenv import load_dotenv
import os
import logging
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import json
import uuid
from termcolor import colored

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("bluetooth")

class BluetoothDiscoveryDaemon(object):

    def __init__(self):
        self.mqtt_client = MQTTClient(self.on_mqtt_message, name="discovery_daemon")
        self.scanner = BLEScanner()
        self.uuid = str(uuid.uuid4())

    async def scan(self):
        await self.scanner.listen_advertisements(self.on_ble_message)

    def check_if_valid_device(self, dev: BLEDevice, manufacturer_id: int = 0) -> list[BLEDevice]:
        """ This funcion updates the internal mac_list. If a MAC address passed the
        checked_mac_address process, it will extend the list 'mac'.
        Arguments:
            devices: device passed by the BleakScanner function

        TODO: check for vendor name or some other idempotent information
        """
            # self.logger.debug(i.metadata)
        if "manufacturer_data" in dev.metadata:
            if manufacturer_id in dev.metadata["manufacturer_data"]:
                logger.info(colored('Device: %s with Address %s discovered!' % (dev.name, dev.address), "green", attrs=['bold']) )
                return True
        return False

    def on_ble_message(self, dev: BLEDevice, properties: AdvertisementData):
        print(dev)
        print(properties)
        manufacturer_id = int(os.environ.get("BLE_MANUFACTURER_ID", 0))
        if self.check_if_valid_device(dev, manufacturer_id=manufacturer_id):
            # return
            self.mqtt_client.send_message(f"{dev.address}/advertisements/{self.uuid}", msg = json.dumps({"device": dev.address, "advertisement_data": str(properties), "metadata": bytes_to_strings(dev.metadata)}))
            self.mqtt_client.send_message(f"{dev.address}/advertisements/name/{self.uuid}", msg = properties.local_name)
            self.mqtt_client.send_message(f"{dev.address}/advertisements/rssi/{self.uuid}", msg = properties.rssi)
            self.mqtt_client.send_message(f"{dev.address}/advertisements/manufacturer_data/{self.uuid}", msg = bytes_to_strings(properties.manufacturer_data[manufacturer_id]))

    def on_mqtt_message(self, topic: str, payload: any):
        pass

load_dotenv()
daemon = BluetoothDiscoveryDaemon()
main_loop = asyncio.get_event_loop()
main_loop.create_task(daemon.scan())
main_loop.run_forever()