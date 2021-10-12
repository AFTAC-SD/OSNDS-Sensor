docker create --name=nodered nodered/node-red
docker cp nodered:/data/. ./nodered
docker rm nodered