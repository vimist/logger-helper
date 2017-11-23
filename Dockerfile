FROM python:3.6-alpine

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt
