# syntax=docker/dockerfile:1
# version 202109240858e3565840c3dc
#FROM python:3.8-slim-buster
FROM ubuntu:20.04
# FROM nvcr.io/nvidia/l4t-base:r32.6.1
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
#ENV https_proxy=http://10.150.206.21:8080
#ENV http_proxy=http://10.150.206.21:8080

#RUN touch /etc/apt/apt.conf
#RUN echo "Acquire::http::Proxy \"http://10.150.206.21:8080\";" > /etc/apt/apt.conf
# RUN export http_proxy=http://10.150.206.21:8080
# RUN export https_proxy=http://10.150.206.21:8080
RUN apt-get update
WORKDIR /app
RUN apt-get install -y vim
RUN apt-get install -y curl
#RUN curl -LJO https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Linux-x86_64.sh
#RUN bash Miniconda3-py38_4.10.3-Linux-x86_64.sh -b
#RUN rm -f Miniconda3-latest-Linux-x86_64.sh 
#RUN apt install python-pip
#RUN apt install python3-pip
COPY requirements.txt requirements.txt
#RUN conda install pip
RUN apt-get install -y python-dev
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade setuptools
RUN apt install -y build-essential
RUN apt-get install -y libssl-dev
# RUN apt install -y pip
RUN pip3 install service_identity
RUN pip3 install -r requirements.txt
#RUN apt-get -y update
#RUN apt-get -y upgrade
COPY functions.py functions.py
COPY main.py main.py
COPY subs.py subs.py
COPY jetson-wheel.tar jetson-wheel.tar
COPY jetson.tar jetson.tar
RUN tar -xzvf jetson.tar
# RUN pip3 install jetson-wheel.tar
#RUN pip3 install docker-compose
#RUN ln -s /usr/local/bin/dockedockr-compose /compose/docker-compose
#COPY docker-compose.yml docker-compose.yml
CMD [ "python3", "main.py" ]
#FROM nodered/node-red
