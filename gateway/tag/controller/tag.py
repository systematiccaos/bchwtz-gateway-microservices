from gateway.tag.tag import Tag
from gateway.mqtt import MQTTClient
from gateway.config import Config
from gateway.tag.tagconfig import TagConfig
from transcoder.utils.encoding import Encoder

class TagController:

    def __init__(self, address: str):
        self.mqtt_client = MQTTClient(self.on_mqtt_message, name="tag_controller")
        self.address = address

    # gets the tags config
    def getConfig(self):
        self.mqtt_client.send_message("%s/command/run_single_ble_command" % self.address, Config.Commands.get_tag_config.value)
    
    # gets the tags current timestamp
    def getTime(self):
        self.mqtt_client.send_message("%s/command/run_single_ble_command" % self.address, Config.Commands.get_tag_timestamp.value)
    
    # gets the tags heartbeat config
    def getHeartbeatConfig(self):
        self.mqtt_client.send_message("%s/command/run_single_ble_command" % self.address, Config.Commands.get_heartbeat_config.value)

    def setTagConfig(self, config: TagConfig):
        self.mqtt_client.send_message("%s/command/run_single_ble_command" % self.address, "%s%s" % (Config.Commands.set_tag_config_substr.value, Encoder.encode_config(config)))
    
    def setTagTime(self, time):
        self.mqtt_client.send_message("%s/command/run_single_ble_command" % self.address, "%s%s" % (Config.Commands.set_tag_time_substr.value, Encoder.encode_time(time)))
    
    def setTagHeartbeat(self, heartbeatinterval):
        self.mqtt_client.send_message("%s/command/run_single_ble_command" % self.address, "%s%s" % (Config.Commands.set_heartbeat_substr.value, Encoder.encode_heartbeat(heartbeatinterval)))

    def startLogging(self):
        self.mqtt_client.send_message("%s/command/run_single_ble_command" % self.address, Config.Commands.activate_logging_at_tag.value)
    
    def startStreaming(self):
        self.mqtt_client.send_message("%s/command/run_single_ble_command" % self.address, Config.Commands.activate_acc_streaming.value)
    
    def stopLogging(self):
        self.mqtt_client.send_message("%s/command/run_single_ble_command" % self.address, Config.Commands.deactivate_logging_at_tag.value)