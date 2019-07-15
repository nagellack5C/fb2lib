FROM alpine:latest

RUN apk add python3

RUN mkdir fb2lib

ADD digger.py ./fb2lib
ADD seeker.py ./fb2lib
ADD wiper.py ./fb2lib
ADD db_operator.py ./fb2lib

WORKDIR fb2lib