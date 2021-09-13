# OSNDS-Docker
## To build the image you run:
 docker build --tag osnds-docker .
## To execute the image into a temporary container with GPIO privileges you run:
 docker run --privileged -it --rm osnds-docker

## Running behind a proxy
 When running behind a proxy several changes needs to be made.
 - curl needs to be proxy enabled on the host machine via 'export http_proxy=proxyip:proxyport' and 'export https_proxy=proxyip:proxyport'
 - to enable the container apt-get install, the Dockerfile needs to be modified to container the line 'RUN echo "Acquire::http::Proxy \"http://proxyip:proxyport\";" > /etc/apt/apt.conf'