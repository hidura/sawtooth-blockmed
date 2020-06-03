FROM ubuntu:xenial

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD && \
    echo 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/bumper/stable xenial universe' >> /etc/apt/sources.list && \
    apt-get update

RUN apt-get install -y sawtooth


RUN apt-get install -y -f -q \
    python3-grpcio-tools \
    python3-setuptools \
    python3-sawtooth-sdk \
    iputils-ping \
    curl \
    telnet \
    python3-pip \
    emacs

RUN pip3 install sqlalchemy flask flask_mail bs4 flask_login flask_sqlalchemy py-postgresql html5lib
RUN mkdir keymanager
COPY keymanager ./keymanager

ENV PATH $PATH:/keymanager
RUN cd keymanager
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
#RUN nohup python3 keymanager/app.py &
