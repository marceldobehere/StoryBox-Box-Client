#!/bin/bash
echo "Date 2: $(date)"
echo "I am $USER, with uid $UID"

# pulseaudio -D

# /usr/bin/aplay /home/marcel/StoryBox-Box-Client/audios/DOWNLOAD_1.mp3

source ~/story-box/env/bin/activate
echo "Date 5: $(date)"


if [ $# -eq 0 ]; then
    python3 -u main.py 
else
    nl=$'\n\n\n'
    echo "${nl}---- START AT $(date) ----${nl}" >> bruh.log
    nohup python3 -u main.py >> bruh.log
fi
