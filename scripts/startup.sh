#!/bin/bash

mongod &
mongod --repair
mongod &


# validate mongodb
# mongo --host 127.0.0.1:27017


# start app
python3.6 run.py  &
