#!/bin/bash

echo "Date 1: $(date)"

cd $(dirname "$0")
ls
pwd

echo "> Doing Autostart"

# echo "> Waiting 2s"
# sleep 2s

echo "> Starting Program"
sudo -H -u marcel bash ./start.sh abc
