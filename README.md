# OSNDS-Docker
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
