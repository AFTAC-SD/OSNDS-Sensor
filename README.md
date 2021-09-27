# OSNDS-Sensor
## To build the image you run:
 docker build --tag osnds-sensor .
 
## To execute the image into a temporary container with GPIO privileges you run:
 docker run --privileged -it --rm osnds-sensor

### For auto start containers modify the container creating to reflect the following:
 docker run --privileged -d --restart=always osnds-sensor

## Running behind a proxy
 When running behind a proxy several changes needs to be made.
 - to enable the container apt-get install, the Dockerfile needs to be modified to container the line 

 RUN echo "Acquire::http::Proxy \\"http://proxyip:proxyport\";" > /etc/apt/apt.conf

 ENV https_proxy=http://10.150.206.21:8080

 ENV http_proxy=http://10.150.206.21:8080

## Other stuff
Added user to the docker group via
sudo usermod -aG docker $USER
Requires a restart or reload to see the changes

Will likely also require the docker.service to start enabled, otherwise it waits for the first docker command to start up:
systemctl enable --now docker.service

you cannot do the fast curl install on arm64 chipsets like xavier, it is unsupported.  you have to perform the following:
apt-get install -y python-dev
apt-get install -y python3-dev
apt install python-pip
apt install python3-pip
pip3 install docker-compose
