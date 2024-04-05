#!/bin/bash

sudo apt-get install -y git build-essential python3-pip python3-setuptools python3-pygame python3-pil
sudo pip3 install --break-system-packages python-osc Adafruit-Blinka adafruit-circuitpython-ssd1306

git clone --recursive https://github.com/libpd/libpd.git /tmp/libpd
cd /tmp/libpd/python
make
sudo make install