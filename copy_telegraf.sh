#!/bin/bash
docker create --name=telegraf telegraf
docker cp telegraf:/etc/telegraf/. ./telegraf
docker rm telegraf