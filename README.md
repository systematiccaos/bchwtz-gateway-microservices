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