from gateway.mqtt import MQTTClient
from gateway.config import Config
import logging
import cmd
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - {%(pathname)s:%(lineno)d}')
logger = logging.getLogger("transcoder")

class CLI(cmd.Cmd):
    def __init__(self):
        super(CLI, self).__init__()
        self.mqtt_client = MQTTClient(self.on_mqtt_message, name="cmd")

    def on_mqtt_message(self, topic: str, payload: any):
            topic_attrs = topic.split("/")
            address = topic_attrs[0]
            self.address = address
            key = ""
            if len(topic_attrs) <= 1 or topic_attrs[1] != "advertisements":
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

    def start_streaming(self, address: str):
        self.mqtt_client.send_message("ble/%s/command/start_streaming" % address)

    def stop_streaming(self, address: str):
        self.mqtt_client.send_message("ble/%s/command/start_streaming" % address)
    
    def get_config(self, address: str):
        """Gets the tags config."""
        self.mqtt_client.send_message("ble/%s/command/run_single_ble_command" % address, Config.Commands.get_tag_config.value)


if __name__ == '__main__':
    CLI().cmdloop()