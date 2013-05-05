#!/usr/bin/env bash

curl -d "email=ahluntang@gmail.com" -d "&notification[from_screen_name]=Started+${BUILD_TAG}" -d "&notification[message]=${BUILD_URL}console" http://boxcar.io/devices/providers/BpWaP5ily2afrrGvKnye/notifications

PATH=.env/bin:$PATH

if [ -d ".env" ]; then
  echo "**> virtualenv exists"
else
  echo "**> creating virtualenv"
  virtualenv .env
fi

pip install -r pip-requires.txt

#./lscale.py generate
coverage run lscale.py generate
coverage report -m
coverage html

nosetests --with-coverage --cover-package=configurator,emulator,generator,utilities
#python -m coverage xml --include=lscale*
pylint -f parseable -d I0011,R0801 lscale | tee pylint.out

curl -d "email=ahluntang@gmail.com" -d "&notification[from_screen_name]=Finished+${BUILD_TAG}" -d "&notification[message]=${BUILD_URL}+${BUILD_URL}console+${BUILD_URL}coveragepy" http://boxcar.io/devices/providers/BpWaP5ily2afrrGvKnye/notifications
