from flask import Flask, jsonify, request
from gateway.mqtt import MQTTClient
from gateway.config import Config
from mergedeep import merge
from transcoder.utils.encoding import Encoder
import time
import json
import os

app = Flask(__name__)
state = {}
def build_dict_from_pth(path: list, val: any) -> dict:
    if len(path) > 1:
        return {path[0]: build_dict_from_pth(path[1:], val)}
    else:
        return  {path[0]: val}

def mqtt_cb(topic:str, msg: bytes):
    merge(state, build_dict_from_pth(topic.split("/"), msg.decode('utf-8')))
    print(state)

mqtt_client = MQTTClient(mqtt_cb, "api")

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Basic Flask API!"

@app.route('/state', methods=['GET'])
def get_items():
    return jsonify(state)

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
    mqtt_client.send_message("%s/command/run_single_ble_command" % address, Encoder().encode_time(time.time()))
    return jsonify({'message': 'pushing current timestamp'})

@app.route('/tag/<address>/get-heartbeat/<int:heartbeat>', methods=['GET'])
def get_heartbeat(address, heartbeat):
    mqtt_client.send_message("%s/command/run_single_ble_command" % address, Encoder().encode_heartbeat(heartbeat))
    return jsonify({'message': 'pulling heartbeat config'})

# @app.route('/item', methods=['POST'])
# def create_item():
#     new_item = request.get_json()
#     new_item['id'] = len(items) + 1
#     items.append(new_item)
#     return jsonify(new_item), 201

if __name__ == '__main__':
    app.run(port=os.environ['API_PORT'], debug=True)