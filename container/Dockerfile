FROM python:3.6-alpine

ARG RELEASE=develop

RUN apk add --no-cache \
        bash \
        man \
        less

RUN pip install --no-cache-dir \
        openpyxl \
        python-dateutil \
        requests \
        xlrd

RUN pip install --no-cache-dir https://github.com/saulpw/visidata/archive/$RELEASE.zip#egg=visidata

RUN adduser -D visidata
WORKDIR /home/visidata

COPY visidatarc .visidatarc
RUN chown -R visidata:visidata .

ENV PAGER="less -SRFX"
USER visidata
ENTRYPOINT ["vd"]
