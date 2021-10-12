#!/bin/bash
docker create --name=grafana grafana/grafana
docker cp grafana:/var/lib/grafana/ ./GF_PATHS_DATA
docker cp grafana:/usr/share/grafana/ ./GF_PATHS_HOME
docker cp grafana:/var/log/grafana/ ./GF_PATHS_LOGS
docker cp grafana:/var/lib/grafana/plugins ./GF_PATHS_PLUGINS
docker cp grafana:/etc/grafana/ ./GF_PATHS_CONFIG
docker rm grafana