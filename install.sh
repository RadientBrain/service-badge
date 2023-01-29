#!/bin/bash
virtualenv -q -p /usr/bin/python3.7.9 service-badge
source service-badge/bin/activate
pip3 install -r requirements.txt