FROM ubuntu:latest

ADD . /impl
WORKDIR /impl/service

RUN apt-get update
RUN apt-get install sudo
RUN ./configure.sh
RUN /bin/bash -c "source env/bin/activate"

CMD ./run.sh 
