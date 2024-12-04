# How to run the development setup
## Quickstart - only has to be ran on first startup:
```bash
cp .env-default .env
python -m venv .venv && source .venv/bin/<your_shell>
pip install -r requirements
```
## Start the microservices - has to be done every time you start developing
### for posix-shells:
```bash
source setpath.sh
```
### if you are using fish:
```bash
source setpath.fish
```
## start docker services
```bash
cd deployments && docker-compose --env-file ../.env up -d
```
## start ble_daemon
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

# Testing in browser:
Now to test, open your browser at the localhost:<API_PORT> - default is localhost:8000/state. This represents the current state of the cluster.

# Architecture:
See [docs/infrastructure.md](docs/infrastructure.md)