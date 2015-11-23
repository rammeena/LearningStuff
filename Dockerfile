FROM ubuntu:latest
EXPOSE 80
RUN apt-get update -y
RUN apt-get install telnet -y
