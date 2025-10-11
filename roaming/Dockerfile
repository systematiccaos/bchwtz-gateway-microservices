FROM python:latest as builder
WORKDIR app
COPY ./roaming/requirements.txt .
COPY ./gateway ./gateway
RUN pip install -r requirements.txt

from builder
COPY ./roaming .
CMD ["python", "roaming_daemon.py"]