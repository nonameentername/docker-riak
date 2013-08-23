# riak
#
# VERSION               0.1

FROM ubuntu:12.04
MAINTAINER Werner R. Mendizabal "werner.mendizabal@gmail.com"

# make sure the package repository is up to date
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update

RUN apt-get install -y openssh-server curl
RUN curl http://apt.basho.com/gpg/basho.apt.key | apt-key add -

RUN bash -c "echo deb http://apt.basho.com precise main > /etc/apt/sources.list.d/basho.list"
RUN apt-get update

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get install -y -q riak || true
RUN mkdir /var/run/sshd
RUN echo 'root:password' | chpasswd

EXPOSE 22 8087 8098

#CMD /usr/sbin/riak start && tail -f /var/log/riak/console.log
CMD /usr/sbin/sshd -D
