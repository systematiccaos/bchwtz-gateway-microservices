FROM python:latest
WORKDIR app
COPY ./gateway ./gateway
COPY ./api .
COPY ./transcoder ./transcoder
RUN pip install -r requirements.txt

CMD ["python", "api.py"]