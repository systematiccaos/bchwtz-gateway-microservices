# Setup

## How to run the development setup on a raspberry pi

### Quickstart - only has to be run on first startup on you raspberry pi in ble-daemon-folder:

```bash
cd ble-daemon
cp .env-default-ble .env
python -m venv .venv && source .venv/bin/activate.<your_shell>
pip install -r requirements
```

### Docker start

```bash
cd deployments
docker compose --env-file ../.env -f docker-compose.yml -f docker-compose.prod.yml up -d # This step will build your containers on the first start 
```

## Development Mode

Head over to localhost:8080 to view the frontend for further information. The API will be available under localhost:8000.

### Start the microservices - has to be done every time you start developing

#### for posix-shells:

```bash
source setpath.sh
```

#### if you are using fish

```bash
source setpath.fish
```

### start docker services

```bash
cd deployments && docker-compose --env-file ../.env up -d
```

### start ble_daemon

```bash
cd ble_daemon && python bluetooth_cmd_daemon.py & bluetooth_discovery_daemon.py
```

## start the transcoder

```bash
bash setpath.sh && cd transcoder && python -m venv .venv && source .venv/bin/<your_shell> && transcoder.py
```

## start the api

```bash
bash setpath.sh && cd transcoder && python -m venv .venv && source .venv/bin/<your_shell> && transcoder.py
```

## Testing in browser

Now to test, open your browser at the localhost:<API_PORT> - default is localhost:8000/state. This represents the current state of the cluster.

## Architecture

See [docs/infrastructure.md](docs/infrastructure.md)

## How to run the setup on a distributed cluster

### Introduction

To run this project on multiple gateways with a centralized api, you should run the central cluster using docker and the ble-services using uv.

## Running the central cluster using docker compose

### On your management server (can be a pi)

First - go ahead and copy .env-default to .env. Change all secrets in this file to a custom value! Then run the following command:

```bash
    cd deployments && docker compose --env-file ../.env up -d
```

### On the raspberri pis

Next we should ssh into the raspberry pis you would like to be gateways. As a primary gateway identifier we are using the hostname of the pi. Make sure to change them to individual values. If you are using raspberry for all your gateways it will not work.
First, clone the project

```bash
    git clone git@github.com:systematiccaos/bchwtz-gateway-microservices.git
```

Next we need to set our PYTHONPATH to match this repository. You can just source the setpath script for your shell.

```bash
    source setpath.sh
```

After that we can copy the .env-default to .env and set up the MQTT-settings to match your main cluster. Don't forget to set the external hostname for your MQTT-server.
  
Make sure you have uv installed. If not run:

```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
```

To run all functions run both ble-daemon-scripts:

```bash
    uv run ble-daemon/bluetooth_cmd_daemon.py & uv run ble-daemon/bluetooth_discovery_daemon.py
```