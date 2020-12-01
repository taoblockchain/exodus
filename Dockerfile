FROM python:3.8-slim
ADD . /

RUN  apt-get update
RUN  apt-get upgrade
RUN  apt-get install python3 ca-certificates -y
RUN  apt-get install build-essential automake autotools-dev autoconf pkg-config gcc git wget -y

WORKDIR /
RUN pip install --upgrade pip \
	&& pip install -r requirements.txt


