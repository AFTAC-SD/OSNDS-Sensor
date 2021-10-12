#!/bin/bash
docker create --name=chronograf chronograf
docker cp chronograf:/etc/default/. ./chronograf/
docker rm chronograf