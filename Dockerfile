FROM alpine:latest

RUN apk add python3

WORKDIR /fb2lib

COPY digger.py .
COPY seeker.py .
COPY wiper.py .
COPY db_operator.py .