FROM python:latest
WORKDIR app
COPY ./gateway ./gateway
COPY ./roaming .
RUN pip install -r requirements.txt

CMD ["python", "roaming_daemon.py"]