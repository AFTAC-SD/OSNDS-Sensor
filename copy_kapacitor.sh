#!/bin/bash
docker create --name=kapacitor kapacitor
docker cp kapacitor:/etc/kapacitor/. ./kapacitor
docker rm kapacitor