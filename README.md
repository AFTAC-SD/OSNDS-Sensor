# OSNDS-Docker
## To build the image you run:
 docker build --tag osnds-docker .
## To execute the image into a temporary container with GPIO privileges you run:
 docker run --privileged -it --rm osnds-docker