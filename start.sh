#!/bin/bash
echo "I am $USER, with uid $UID"
pwd
ls
pulseaudio -D

source ~/env/bin/activate
python3 main.py