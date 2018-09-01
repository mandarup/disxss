

# Pull base image.
FROM ubuntu:16.04

#COPY ../requirements.txt /tmp/requirements.txt
COPY requirements.txt /tmp/requirements.txt

# Define mountable directories.
VOLUME ["/app", "/data/db"]

# Define working directory.
WORKDIR /app

RUN echo $pwd

RUN apt-get update -y && \
    apt-get install apt-transport-https -y


RUN apt-get update
RUN apt-get install -y software-properties-common # vim
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv
RUN apt-get install -y git

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel
RUN python3.6 -m pip install --upgrade jupyter flask pymongo

# install requirements
RUN python3.6 -m pip install -r /tmp/requirements.txt


# Install MongoDB.
RUN \
  apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4 && \
  echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.0 multiverse" |  tee /etc/apt/sources.list.d/mongodb-org-4.0.list  && \
  apt-get update -y && \
  apt-get install -y mongodb-org && \
  rm -rf /var/lib/apt/lists/*


# Define default command.
CMD ["mongod &"]

RUN cd /app/disxss

# Expose ports.
#   - 27017: process
#   - 28017: http
EXPOSE 27017
EXPOSE 28017
