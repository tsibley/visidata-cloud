FROM python:3.6-alpine

ARG RELEASE=develop

RUN apk add --no-cache \
        man \
        less

RUN pip install --no-cache-dir \
        openpyxl \
        python-dateutil \
        requests \
        xlrd

RUN pip install --no-cache-dir https://github.com/saulpw/visidata/archive/$RELEASE.zip#egg=visidata

RUN adduser -D visidata
USER visidata
WORKDIR /home/visidata

COPY visidatarc .visidatarc

ENV PAGER="less -SRFX"

ENTRYPOINT ["vd"]
