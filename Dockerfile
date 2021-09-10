# syntax=docker/dockerfile:1

#FROM python:3.8-slim-buster
FROM ubuntu:20.04
# FROM nvcr.io/nvidia/l4t-base:r32.6.1
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

WORKDIR /app
RUN apt-get install -y vim
# COPY Miniconda3-py38_4.10.3-Linux-x86_64.sh Miniconda3-py38_4.10.3-Linux-x86_64.sh
# RUN bash Miniconda3-py38_4.10.3-Linux-x86_64.sh -b
RUN apt-get install -y curl
RUN curl -LJO https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Linux-x86_64.sh
RUN bash Miniconda3-py38_4.10.3-Linux-x86_64.sh -b
RUN rm -f Miniconda3-latest-Linux-x86_64.sh 
# && mkdir /root/.conda && bash Miniconda3-latest-Linux-x86_64.sh -b && rm -f Miniconda3-latest-Linux-x86_64.sh 

COPY requirements.txt requirements.txt
RUN conda install pip
RUN apt-get install -y python-dev
RUN apt-get install -y python3-dev
# RUN conda install --file requirements.txt
RUN apt install -y build-essential
RUN apt-get install -y libssl-dev
RUN pip3 install service_identity
RUN pip3 install -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade



COPY functions.py functions.py
COPY main.py main.py
CMD [ "python3", "main.py" ]