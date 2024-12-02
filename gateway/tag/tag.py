import asyncio
from binascii import hexlify
from datetime import datetime
from typing import Callable, Type
import time
from typing_extensions import Self
from xmlrpc.client import DateTime
from bleak.backends.device import BLEDevice
from gateway.sensor.acceleration import AccelerationSensor
from gateway.sensor.barometer import BarometerSensor
from gateway.sensor.temperature import TemperatureSensor
from gateway.sensor.humidity import HumiditySensor
from gateway.sensor.battery import BatterySensor
from gateway.tag.tag_interface.encoder import Encoder
from gateway.tag.tagconfig import TagConfig
from gateway.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from gateway.config import Config
import logging
from gateway.tag.tag_interface.decoder import Decoder
from bleak.backends.scanner import AdvertisementData
import aiopubsub
from paho.mqtt.client import Client, MQTTMessage
import json
from gateway.util.signal_last import signal_last


from gateway.sensor.sensor import Sensor
from gateway.tag.tag_interface.signals import SigScanner

class Tag(object):
    """ Shadow of a hardware tag. What is a tag compared to a sensor? A tag has different kinds of sensors, a microcontroller (NRF52) and additional hardware like the battery-holder etc. A sensor is simply one device on the tag, responsible of measuring something.
    """
    def __init__(self, name: str = "", address: str = "", device: BLEDevice = None, online: bool = True, pubsub_hub: aiopubsub.Hub = None, mqtt_client: Client = None) -> None:
        """ Initializes a new tag.
            Arguments:
                name: the bluetooth-name of the tag
                address: the mac-address of the tag
                device: the bleak-device (bleak is a ble-library that helps us to wrap bluez - this is the linux ble daemon)
                online: is the device online at the moment (in reach of this gateway)
                pubsub_hub: some gateway-internal pubsub-communication for events
        """
        self.name: str = name
        self.address: str = address
        self.ble_device: BLEDevice = device
        self.metadata: dict[str, dict[int, bytes]] = None
        self.ble_conn: BLEConn = BLEConn()
        self.logger = logging.getLogger()
        self.configured: bool = False
        self.logging_active: bool = False
        # TODO: add sensors as ble caps on firmware side to autoload sensor classes by names
        self.sensors: list[Sensor] = [
            AccelerationSensor(),
            BarometerSensor(),
            TemperatureSensor(),
            HumiditySensor(),
            BatterySensor(),
        ]
        self.dec: Decoder = Decoder()
        self.enc: Encoder = Encoder()
        self.config: TagConfig = None
        self.heartbeat: int = 0
        self.time: float = 0.0
        self.online: bool = online
        self.acc_log_res_topic: str = Config.MQTTConfig.topic_tag_prefix.value + "/" + self.address + Config.MQTTConfig.topic_tag_cmd_get_acceleration_log_res.value
        self.acc_stream_topic: str = Config.MQTTConfig.topic_tag_prefix.value + "/" + self.address + Config.MQTTConfig.topic_tag_cmd_get_acceleration_stream_res.value
        self.acc_log_req_id: str = ""
        self.seen_in_last_iter: bool = False
        self.last_seen: float = time.time()
        self.pubsub_hub: aiopubsub.Hub = pubsub_hub
        self.publisher: aiopubsub.Publisher = aiopubsub.Publisher(self.pubsub_hub, prefix = aiopubsub.Key("TAG"))
        self.mqtt_client: Client = mqtt_client
        if self.mqtt_client is not None:
            self.subscribe_to_mqtt_chans()

    def read_sensor_data(self, data: AdvertisementData = None):
        """ Calls the read_data_from_advertisement on all its sensors.
            Arguments:
                data: AdvertisementData as a dict
        """
        if data is None:
            return
        tag_data = self.dec.decode_advertisement(data)
        if tag_data == None:
            return
        for sensor in self.sensors:
            sensor.read_data_from_advertisement(tag_data)
            # submit mqtt vals for accelerometer
            accelerometer = self.get_sensor_by_type(AccelerationSensor)
            if len(accelerometer.measurements) > 0:
                self.mqtt_client.publish("%s/%s/%s/acc_x" % (Config.MQTTConfig.topic_tag_prefix.value, self.address, accelerometer.__class__.__name__), next(reversed(accelerometer.measurements)).acc_x)
                self.mqtt_client.publish("%s/%s/%s/acc_y" % (Config.MQTTConfig.topic_tag_prefix.value, self.address, accelerometer.__class__.__name__), next(reversed(accelerometer.measurements)).acc_y)
                self.mqtt_client.publish("%s/%s/%s/acc_z" % (Config.MQTTConfig.topic_tag_prefix.value, self.address, accelerometer.__class__.__name__), next(reversed(accelerometer.measurements)).acc_z)
            # submit mqtt vals for voltage
            vbat = self.get_sensor_by_type(BatterySensor)
            if len(vbat.measurements) > 0:
                self.mqtt_client.publish("%s/%s/%s/voltage" % (Config.MQTTConfig.topic_tag_prefix.value, self.address, vbat.__class__.__name__), next(reversed(vbat.measurements)).voltage)
            # submit mqtt vals for athmospheric pressure
            press = self.get_sensor_by_type(BarometerSensor)
            if len(press.measurements) > 0:
                self.mqtt_client.publish("%s/%s/%s/pressure" % (Config.MQTTConfig.topic_tag_prefix.value, self.address, press.__class__.__name__), next(reversed(press.measurements)).pressure)
            # submit mqtt vals for humidity
            hum = self.get_sensor_by_type(HumiditySensor)
            if len(hum.measurements) > 0:
                self.mqtt_client.publish("%s/%s/%s/humidity" % (Config.MQTTConfig.topic_tag_prefix.value, self.address, hum.__class__.__name__), next(reversed(hum.measurements)).humidity)
            # submit mqtt vals for temperature
            temp = self.get_sensor_by_type(TemperatureSensor)
            if len(temp.measurements) > 0:
                self.mqtt_client.publish("%s/%s/%s/temperature" % (Config.MQTTConfig.topic_tag_prefix.value, self.address, temp.__class__.__name__), next(reversed(temp.measurements)).temperature)

    def get_sensors_props(self) -> list[dict]:
        """ Making the object's sensors serializable.
            Returns:
                all sensor properties as a list of dicts
        """
        sensors = [dict]
        for s in self.sensors:
            sensors.append(s.get_props())
        return sensors
    
    def get_sensor_by_type(self, T: Type) -> Sensor:
        """ Gets a sensor by its type, e.g. AccelerationSensor and returns it
            Arguments:
                T: type of the searched sensor
            Returns:
                either None or the sensor object
        """
        for sensor in self.sensors:
            if type(sensor) is T:
                return sensor
        return None

    def get_props(self) -> dict:
        """ Making the tag serializable.
            Returns:
                self as dict
        """
        return {'name': self.name, 'address': self.address, 'sensors': self.get_sensors_props(), 'time': self.time, 'config': self.config, 'online': self.online, 'last_seen': self.last_seen}

    def subscribe_to_mqtt_chans(self):
        """ Connect callback for mqtt.
        """
        self.logger.info("connected to mqtt")
        pre = Config.MQTTConfig.topic_tag_prefix.value
        ownprefix = pre + "/" + self.address + "/commands/"
        commands = Config.MQTTConfig.tag_commands.value
        for cmd in commands:
            sub = ownprefix + cmd
            if self.mqtt_client is not None:
                self.mqtt_client.subscribe(sub, 0)
            self.logger.info(sub)

    def __return_paged_measurements(self, req_id: int):
        for sensor in self.sensors:
            measurements = []
            for idx, measurement in enumerate(sensor.measurements):
                measurements.append(measurement)
                if idx % 10 == 0 or len(sensor.measurements) - idx < 10:
                    if self.mqtt_client is not None:
                        self.mqtt_client.publish(
                            Config.MQTTConfig.topic_tag_prefix.value + "/" + self.address + "/" + sensor.name + "/" + req_id,
                            payload=json.dumps({
                                "obj_type": "measurement",
                                "ongoing_request": True,
                                "request_id": req_id,
                                "payload": {
                                    "status": "success",
                                    "tag_address": self.address,
                                    "measurement": measurements
                            }}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4), retain=True)
                    measurements = []
