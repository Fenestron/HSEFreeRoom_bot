#!/usr/bin/env bash

# Install some packages

sudo apt-get update ; sudo apt-get upgrade
sudo apt-get install openssl python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install cherrypy pytelegrambotapi pymongo

# Install MongoDb

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6

# Ubuntu 16.04
echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list

sudo apt-get update

sudo apt-get install -y mongodb-org

sudo service mongod start

# Create a certificate

openssl genrsa -out webhook_pkey.pem 2048

echo
echo "=================================="
echo "Сейчас вам будет предложено ввести некоторую информацию о себе."
echo "Можете везде ввести \".\" кроме поля Common Name."
echo "В поле Common Name необходимо ввести следующий адрес:"
echo "=================================="
echo
# Узнать свой внешний ip-адрес
wget -qO- eth0.me

openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem

