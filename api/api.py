import logging
import eventlet
eventlet.monkey_patch()
from flask import Flask, jsonify
from flask_cors import CORS
from gateway.mqtt import MQTTClient
from gateway.config import Config
from mergedeep import merge
from transcoder.utils.encoding import Encoder
from datetime import datetime
import os
from flask_socketio import SocketIO

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - {%(pathname)s:%(lineno)d}')
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)
state = {}

def build_dict_from_pth(path: list, val: any) -> dict:
    if len(path) > 1:
        return {path[0]: build_dict_from_pth(path[1:], val)}
    else:
        return  {path[0]: val}

def mqtt_cb(topic:str, msg: bytes):
    merge(state, build_dict_from_pth(topic.split("/"), msg.decode('utf-8')))
    logger.info(state)
    socketio.emit("state", state)

mqtt_client = MQTTClient(mqtt_cb, "api", asnc=False, nostart=True)
socketio.start_background_task(mqtt_client.client.loop_forever)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Basic Flask API!"

@app.route('/get-state', methods=['GET'])
def get_state():
    return jsonify(state)

@app.route('/get-tags', methods=['GET'])
def get_tags():
    return jsonify([tag for tag, val in state.items()])

@app.route('/tag/<address>/get-config', methods=['GET'])
def get_config(address):
    mqtt_client.send_message("%s/command/run_single_ble_command" % address, Config.Commands.get_tag_config.value)
    return jsonify({'message': 'pulling config'})

@app.route('/tag/<address>/get-time', methods=['GET'])
def get_time(address):
    mqtt_client.send_message("%s/command/run_single_ble_command" % address, Config.Commands.get_tag_timestamp.value)
    return jsonify({'message': 'pulling timestamp'})

@app.route('/tag/<address>/set-current-time', methods=['GET'])
def set_time(address):
    raw_time = int(datetime.now().timestamp()) * 1000
    logger.info(f"raw time: {raw_time}")
    encoded_time = Encoder().encode_time(raw_time)
    logger.info(f"encoded time: {encoded_time}")
    mqtt_client.send_message("%s/command/run_single_ble_command" % address, encoded_time)
    return jsonify({'message': 'pushing current timestamp'})

@app.route('/tag/<address>/get-heartbeat', methods=['GET'])
def get_heartbeat(address):
    mqtt_client.send_message("%s/command/run_single_ble_command" % address, Config.Commands.get_heartbeat_config.value)
    return jsonify({'message': 'pulling heartbeat config'})

@app.route('/tag/<address>/set-heartbeat/<int:heartbeat>', methods=['GET'])
def set_heartbeat(address, heartbeat):
    mqtt_client.send_message("%s/command/run_single_ble_command" % address, Encoder().encode_heartbeat(heartbeat))
    return jsonify({'message': 'pushing heartbeat config'})

@app.route('/tag/<address>/get-acc-log', methods=['GET'])
def get_acceleration_log(address):
    mqtt_client.send_message("%s/command/run_single_ble_command" % address, Config.Commands.get_acceleration_data.value)
    return jsonify({'message': 'pulling acceleration log'})

@app.route('/tag/<address>/start-logging', methods=['GET'])
def start_acceleration_log(address):
    mqtt_client.send_message("%s/command/run_single_ble_command" % address, Config.Commands.activate_logging_at_tag.value)
    return jsonify({'message': 'pulling acceleration log'})

@app.route('/tag/<address>/start-streaming', methods=['GET'])
def start_streaming(address):
    mqtt_client.send_message("%s/command/start_streaming" % address)
    return jsonify({'message': 'pulling acceleration log'})

@app.route('/tag/<address>/stop-streaming', methods=['GET'])
def stop_streaming(address):
    mqtt_client.send_message("%s/command/stop_streaming" % address)
    return jsonify({'message': 'pulling acceleration log'})

# @app.route('/item', methods=['POST'])
# def create_item():
#     new_item = request.get_json()
#     new_item['id'] = len(items) + 1
#     items.append(new_item)
#     return jsonify(new_item), 201
@socketio.on('connect')
def connect():
    print("client connected")
    socketio.emit("successfully connected")

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
if __name__ == '__main__': 
    socketio.run(app, host="0.0.0.0", port=int(os.environ["API_PORT"]))