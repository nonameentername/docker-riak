# riak
#
# VERSION               0.1

FROM ubuntu:12.04
MAINTAINER Werner R. Mendizabal "werner.mendizabal@gmail.com"

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update

RUN apt-get install -y curl

RUN curl https://packagecloud.io/gpg.key | apt-key add -

RUN apt-get install -y apt-transport-https

ENV FILENAME /etc/apt/sources.list.d/basho.list
ENV OS ubuntu
ENV DIST precise
ENV PACKAGE_CLOUD_RIAK_DIR https://packagecloud.io/install/repositories/basho/riak

RUN curl "${PACKAGE_CLOUD_RIAK_DIR}/config_file.list?os=${OS}&dist=${DIST}&name=$(hostname -f)" > $FILENAME

RUN apt-get update

RUN apt-get install -y logrotate riak

ADD files/run.sh /

EXPOSE 8087 8098

CMD ./run.sh
