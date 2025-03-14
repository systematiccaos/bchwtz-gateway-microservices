from gateway.mqtt import MQTTClient
from bluetooth import BLEConn
import asyncio
from dotenv import load_dotenv
import os
import socket
import logging
from gateway.json_helper import bytes_to_strings
import hashlib
import threading


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
        self.hostname = socket.gethostname()
        self.ipaddr = hashlib.sha256(socket.gethostbyname(self.hostname).encode('utf-8')).hexdigest()
        self.mqtt_client.send_message(f"log", msg = "%s command daemon online" % self.ipaddr)
        self.ble_clients = {}

    def on_ble_response(self, status: int, response: bytearray):
        res = bytes_to_strings(response)
        logger.info(res)
        self.mqtt_client.send_message(f"{self.address}/response/{self.ipaddr}", msg = res)

    def on_stream_data(self, status: int, response: bytearray):
        res = bytes_to_strings(response)
        logger.info(res)
        # res = res[1:]
        self.mqtt_client.send_message(f"{self.address}/stream/{self.ipaddr}", msg = res)

    def on_mqtt_message(self, topic: str, payload: bytes):
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
        if address not in self.ble_clients.keys():
            ble_client = BLEConn(address=address)
            self.ble_clients[address] = ble_client
            logger.info(self.ble_clients)
        else:
            ble_client = self.ble_clients[address]
        logger.debug(payload)
        try:
            if fn == "run_single_ble_command":
                logger.info("running command")
                logger.info(payload)
                asyncio.run_coroutine_threadsafe(ble_client.run_single_ble_command(read_chan=os.environ.get("BLE_READ_CH"), write_chan=os.environ.get("BLE_WRITE_CH"), cmd = payload, cb=self.on_ble_response, await_response=True), ble_loop)
            elif fn == "start_stream":
                asyncio.run_coroutine_threadsafe(ble_client.run_single_ble_command(read_chan=os.environ.get("BLE_READ_CH"), write_chan=os.environ.get("BLE_WRITE_CH"), cmd = payload, cb=self.on_stream_data, await_response=False), ble_loop)
            elif fn == "stop_stream":
                ble_client.stopEvent.set()
            else:
                logger.debug(f"function not available for {fn}")
            # ble_loop.run_until_complete()
            # self.loop.run_until_complete(ble_client.connect())
        except Exception as e:
            logger.error(f"recovered from ble error - check your command")
            logger.exception(e)
            self.mqtt_client.send_message("%s/response/error/%s" % (address, self.ipaddr), "error")
            return

load_dotenv()
daemon = BluetoothCMDDaemon()
t = threading.Thread(target=ble_loop.run_forever)
t.start()
main_loop.run_forever()