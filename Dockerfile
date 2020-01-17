FROM python:3.6-alpine

ARG BRANCH=develop

RUN pip install --no-cache-dir \
        openpyxl \
        python-dateutil \
        requests \
        xlrd

RUN pip install --no-cache-dir https://github.com/saulpw/visidata/archive/$BRANCH.zip#egg=visidata

ENTRYPOINT ["vd"]
