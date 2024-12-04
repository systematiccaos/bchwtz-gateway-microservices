from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
import asyncio
import logging
from typing import Callable

class BLEConn():
    """ Wraps bleak to be easily accessible for the gateway's usecase and to be able to use custom logging.
    """
    def __init__(self, address) -> None:
        """ creates a new instance of BLEConn.
        """
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - {%(pathname)s:%(lineno)d}')
        self.logger: logging.Logger = logging.getLogger("BLEConn")
        self.logger.setLevel(logging.INFO)
        self.stopEvent: asyncio.Event = asyncio.Event()
        self.stopEvent.clear()
        self.client: BleakClient = None
        self.device: BLEDevice = None
        self.address: str = address

    async def _get_client(self, dev: str, timeout: float = 30.0) -> BleakClient:
        if self.client is None or not self.client.is_connected:
            self.client = BleakClient(dev)
            # await self.client.disconnect()

            if not self.client.is_connected:
                try:
                    self.logger.info("connecting to %s", dev)
                    await self.client.connect(timeout=30.0)
                    self.logger.info("successfully connected to %s", dev)
                except Exception as e:
                    self.logger.error("could not connect to %s - retry pending...", dev)
                    self.logger.error(e)
                    await self.client.disconnect()
                    await self._get_client(dev=dev, timeout=timeout+5.0)
        else:
            self.logger.info("was already connected to %s", dev)
        return self.client

    async def disconnect(self):
        await self.client.disconnect()

    async def run_single_ble_command(self, read_chan: str, write_chan: str, cmd: bytes, timeout: float = 20.0, cb: Callable[[int, bytearray], None] = None, retries: int = 0, max_retries: int = 5, await_response: bool = True):
        """ Connects to a given tag and starts notification of the given callback
        Arguments:
            tag: communication device abstraction
            timeout: how long should one run of the function take?
            b: Callback that will be executed when a notification is received
        """
        self.logger.info("connecting to %s", self.address)
        device: BLEDevice = await BleakScanner.find_device_by_address(self.address, timeout=5.0)
        cmd = cmd.decode('ascii')
        # self.logger.info(device.details)
        async with self.connect(device) as client:
            # if not device.details["props"]["Paired"]:
            #     await client.pair()
            self.logger.info("connected to %s", self.address)
            self.logger.info("sending command %s", cmd)
            self.logger.info("raw %s", bytearray.fromhex(cmd))
            
            try:
                if cb is not None:
                    await client.start_notify(char_specifier = read_chan, callback = cb)
                await client.write_gatt_char(write_chan, bytearray.fromhex(cmd), await_response)
                if await_response:
                    self.logger.info("disconnecting...")
                else:
                    self.logger.info("waiting for data...")
                    await self.stopEvent.wait()
                self.logger.info("ending...")
                self.stopEvent.clear()

            except Exception as e:
                if retries < max_retries:
                    self.logger.warn(f"{e} - retrying...")
                    await self.run_single_ble_command(self.device, read_chan, write_chan, cmd, timeout, cb, retries+1, max_retries)
                return
            
    def connect(self, device: BLEDevice) -> BleakClient:
        if self.client is None or not self.client.is_connected:
            self.client = BleakClient(device)
        return self.client

    async def listen_for_data_stream(self, read_chan: str, timeout: float = 20.0, cb: Callable[[int, bytearray], None]=None):
        device: BLEDevice = await BleakScanner.find_device_by_address(self.address, timeout=5.0)
        client = self.connect(device)
        await client.start_notify(char_specifier = read_chan, callback = cb)
        self.logger.info("started listening for stream data...")
        await self.stopEvent.wait()
        self.logger.info("stopped listening for stream data")
        await self.stopEvent.clear()
        await client.stop_notify(char_specifier=read_chan)

class BLEScanner():
    async def listen_advertisements(timeout: float = 5.0, cb: Callable[[BLEDevice, dict], None] = None) -> None:
        """ Starts listening for advertisements.
            Arguments:
                timeout: specifies how long the listening should be running
                cb: Callback that is called on every advertisement that is discovered
        """
        scanner = BleakScanner(detection_callback = cb)
        await scanner.start()

    async def scan_tags(manufacturer_id: int = 0, timeout: float = 20.0) -> list[BLEDevice]:
        """The function searches for bluetooth devices nearby and passes the
            MAC addresses to the validate_manufacturer function.
            Arguments:
                timeout: timeout for the find_tags function
            Returns:
                A list of BLEDevice that can be used by other parts of the software now
        """
        devicelist = []
        devices = await BleakScanner.discover(timeout=timeout)
        return devicelist