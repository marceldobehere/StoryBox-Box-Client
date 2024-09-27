#!/bin/bash
python -m venv ~/story-box/env
./install.sh mfrc522
./install.sh RPi.GPIO 
./install.sh spidev 
./install.sh python-vlc 
./install.sh requests
