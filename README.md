# WIP
Quickstart:
```bash
cd ble_daemon && cp .env-default .env
```
```bash
source setpath.sh
```
if you are using fish:
```bash
source setpath.fish
```
```bash
cd deployments && cp .env-default .env && docker-compose --env-file .env up -d
```
````bash
cd ble_daemon && python -m venv .venv && source .venv/bin/<your_shell> && python bluetooth_cmd_daemon.py & bluetooth_discovery_daemon.py
```
````bash
bash setpath.sh && cd transcoder && python -m venv .venv && source .venv/bin/<your_shell> && transcoder.py
```