#!/bin/bash
docker create --name=nodered nodered/node-red
docker cp nodered:/date/. ./nodered
docker rm nodered