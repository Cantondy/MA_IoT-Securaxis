FROM rust:slim-buster
#FROM python:3.7-buster
RUN apt-get -y update
RUN apt-get -y install python3-pip
#RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
RUN apt-get -y install build-essential libssl-dev libffi-dev python-dev
RUN apt install --fix-broken
RUN pip3 install --upgrade pip
RUN pip3 install paho-mqtt
RUN pip3 install --upgrade cryptography
RUN pip3 install azure.storage.blob
COPY app.py /

CMD ["python3", "-u", "app.py"]
