#!/bin/bash
echo "Date 2: $(date)"
echo "I am $USER, with uid $UID"

# pulseaudio -D

# /usr/bin/aplay /home/marcel/StoryBox-Box-Client/audios/DOWNLOAD_1.mp3

source ~/story-box/env/bin/activate
echo "Date 5: $(date)"

# python3 main.py -u | tee /tmp/story-box-py.log
# stdbuf -i0 -o0 -e0 python3 main.py -u > /tmp/story-box-py.log
# python3 main.py -u | tee /tmp/story-box-py.log
python3 main.py -u 
# > /tmp/story-box-py.log
