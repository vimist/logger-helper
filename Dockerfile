FROM python:3.6-alpine

RUN apk --no-cache add make

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt
