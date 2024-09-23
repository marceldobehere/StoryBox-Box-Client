#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep
import vlc
import os
import os.path
import json

# 0 - RED, 1 - YELLOW
buttons = [3, 5]
def initButtons():
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    for id in buttons:
        GPIO.setup(id, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def getBtn(idx):
    return GPIO.input(buttons[idx]) == 0

initButtons()


def readFile(path):
    f = open(path, "r")
    return f.read()

def writeFile(path, text):
    f = open(path, "w")
    f.write(text)
    f.close()

def readFileOrDef(path, defaultText):
    if not os.path.isfile(path):
        writeFile(path, defaultText)
    return readFile(path)

serialCode = ""
accountCode = ""
playlist = {}
testPlayList = {
    "12345": "draw.mp3",
    "874127460810": "t.mp3",
    "338358677895": "nokia klingel.wav",
    "682123768128": "scream.mp3",
    "528310846334": "bruh.wav",
    "541262328181": "fart-2.wav"
}

def initData():
    global serialCode, accountCode, playlist

    serialCode = readFileOrDef("./data/serial_code.txt", "SERIAL-12345-TEST")
    print("> Serial Code: " + serialCode)

    accountCode = readFileOrDef("./data/account_code.txt", "ACCOUNT-BRUH_12345-TEST")
    print("> Account Code: " + accountCode)

    playlistStr = readFileOrDef("./data/song_map.json", json.dumps(testPlayList, indent=4))
    playlist = json.loads(playlistStr)
    print("> Playlist: " + json.dumps(playlist))


try:
    initData()
except Exception as error:
    print("ERROR DURING INIT: " + str(error))
    exit(-1)








def mainLoop():
    reader = SimpleMFRC522()
    print('Ready')


    exit = False
    while not exit:
        try:
            print('> Waiting for Chip:')

            id, text = reader.read_no_block()
            if id:
                tryPlaySound(id)
                continue
            
            if getBtn(1):
                tryPlaySound(12345)
                continue
                
            sleep(0.1)
        finally:
            pass
    GPIO.cleanup()

def getFileFromId(id):
    res = playlist.get(str(id))
    print('"' + str(id) + '" -> ' + str(res) + " " + str(playlist))
    if res == None:
        return ""
    else:
        return res

def tryPlaySound(id):
    print(' > Attempting to play from ID: ' + str(id))
    filename = getFileFromId(id)
    if filename == "":
        print(' > Unkown ID!')
        sleep(1)
        return
    print(" > Playing: " + filename)

    player = vlc.MediaPlayer("./test_audio/"+filename)
    player.audio_set_volume(100)
    
    print('  > Play')
    player.play()
    
    print('  > Wait')
    Ended = 6
    while True:
        if player.get_state() == Ended:
            break
        if getBtn(0):
            print('  > Force Stop')
            break
        sleep(0.1)

    print('  > Stop')
    player.stop()



tryPlaySound(12345)
mainLoop()



# try:
#     id, text = reader.read()
#     print(id)
#     print(text)
# finally:
#     pass

# try:
#     text = input('New data:')
#     print("Now place your tag to write")
#     # reader.write(text)
#     print("Written")
# finally:
#     pass


# GPIO.cleanup()


