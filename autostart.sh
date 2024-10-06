#!/bin/bash

cd $(dirname "$0")
ls
pwd

echo "> Doing Autostart"

# echo "> Waiting 2s"
# sleep 2s

echo "> Starting Program"
# sudo -H -u marcel bash ./start.sh
sudo bash ./start2.sh
# sudo python3 main.py
