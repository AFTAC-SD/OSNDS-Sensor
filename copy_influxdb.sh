#!/bin/bash
docker create --name=influxdb influxdb:1.8.9
docker cp influxdb:/etc/influxdb/. ./influxdb
docker cp influxdb:/var/lib/influxdb/. ./influxdb_config
docker rm influxdb