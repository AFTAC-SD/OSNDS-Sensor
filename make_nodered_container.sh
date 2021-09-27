#!/bin/bash
mkdir /home/xavier/nodered/
docker run --name=nodered nodered/node-red
docker cp nodered:/data/ /home/xavier/nodered/
docker stop nodered
docker rm nodered
docker run -d --privileged -v /home/xavier/nodered/:/data --restart=always --name=nodered -p 1880:1880/tcp nodered/node-red

