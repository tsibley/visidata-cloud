FROM python:3.6-alpine

ARG RELEASE=develop

RUN apk add --no-cache \
        bash \
        mandoc \
        less

RUN pip install --no-cache-dir \
        openpyxl \
        python-dateutil \
        requests \
        s3fs \
        xlrd

RUN pip install --no-cache-dir https://github.com/saulpw/visidata/archive/$RELEASE.zip#egg=visidata

RUN adduser -D visidata

# /home/visidata will be overlayed as a tmpfs in each container, so anything we
# put there in the image won't actually be available.  Instead, locate the
# typical ~/.visidata/ dir and ~/.visidatarc file in /etc.
COPY visidata /etc/visidata
COPY visidatarc /etc/visidatarc

# Install plugins
ADD https://raw.githubusercontent.com/ajkerrigan/visidata-plugins/1f0ff2a8610a1f5f6ffe56634688e60d21b72728/plugins/vds3.py \
    /etc/visidata/plugins/

RUN chown -R visidata:visidata /etc/visidata /etc/visidatarc

ENV PAGER="less -SRFX"

USER visidata
WORKDIR /home/visidata
ENTRYPOINT ["vd", "--visidata-dir=/etc/visidata", "--config=/etc/visidatarc", "--quitguard"]
