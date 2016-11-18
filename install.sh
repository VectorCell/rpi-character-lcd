#!/bin/bash

APTPROG=apt
if [ -z "$(which $APTPROG)" ]; then
	APTPROG=apt-get
fi

sudo $APTPROG install build-essential python3 python3-dev python3-pip python3-smbus i2c-tools
sudo pip3 install RPi.GPIO

if [ ! -d Adafruit_Python_CharLCD ]; then
	git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
	cd Adafruit_Python_CharLCD
	sudo python3 setup.py install
	cd -
fi

echo
echo "Please make sure that you enable I2C support by running 'sudo raspi-config' and selecting 'Advanced Options'"
sudo i2cdetect -y 1
