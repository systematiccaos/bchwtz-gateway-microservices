FROM python:latest
WORKDIR /app
COPY ./transcoder .
COPY ./gateway ./gateway
RUN pip install -r requirements.txt

CMD ["python", "transcoder.py"]