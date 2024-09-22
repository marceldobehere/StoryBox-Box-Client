#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep

import vlc



def mainLoop():
    reader = SimpleMFRC522()
    print('Ready')

    exit = False
    while not exit:
        try:
            print('> Waiting for Chip:')
            id, text = reader.read()
            tryPlaySound(id)
        finally:
            pass
    GPIO.cleanup()

def getFileFromId(id):
    if id == 528310846334:
        return "bruh.wav"
    if id == 682123768128:
        return "scream.mp3"
    if id == 338358677895:
        return "nokia klingel.wav"
    if id == 12345:
        return "draw.mp3"
    return ""

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
        sleep(0.5)

    print('  > Stop')
    player.stop()



tryPlaySound(12345)

mainLoop()


# print('Music')
# player = vlc.MediaPlayer("bruh.wav")
# player.audio_set_volume(200)

# print('Play')
# player.play()
# sleep(1)

# print('Pause')
# player.pause()
# sleep(1)

# print('Play')
# player.play()
# sleep(1)

# print('Stop-')
# player.stop()

# print('Hello')

# exit()



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


