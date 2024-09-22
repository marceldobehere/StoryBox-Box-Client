#!/bin/bash

cd $(dirname "$0")
ls
pwd

echo "> Doing Autostart"

echo "> Waiting 5s"
sleep 5s

echo "> Starting Program"
sudo -H -u marcel bash ./start.sh