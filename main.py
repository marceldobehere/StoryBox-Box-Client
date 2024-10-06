#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep
from subprocess import call

import src.files as files
import src.audio as audio
import src.btn as btn
import src.boxData as boxData
import src.network as network
import src.syncStuff as syncStuff

LOW_POWER_MODE = False
def setLowPowerMode(state):
    global LOW_POWER_MODE
    LOW_POWER_MODE = True
    print("> Set Low Power Mode To: ", LOW_POWER_MODE)


try:
    btn.initButtons()
    boxData.initBoxData()
    audio.initPlaylistData()
except Exception as error:
    print("ERROR DURING INIT: " + str(error))
    exit(-1)
setLowPowerMode(True)

def powerOff():
    print("> Shutting off")
    print(" > Result: ", call("sudo nohup shutdown -h now", shell=True))

def mainLoop():
    reader = SimpleMFRC522()
    print('Ready')

    exit = False
    while not exit:
        try:
            # print('> Waiting for Chip:')

            id, text = reader.read_no_block()
            if id:
                audio.tryPlayPlaylist(id)
                sleep(0.5)
                continue
            
            if btn.getBtn(1):
                audio.tryPlayFile("./OLD/draw.mp3")
                continue
            
            if not btn.getBtn(2):
                powerOff()
                continue
            
            if LOW_POWER_MODE:
                sleep(1.1)
            else:
                sleep(0.1)
        finally:
            pass
    GPIO.cleanup()


# print("File Test: " + str(network.getTestFile(2)))

# syncStuff.performSync()
#syncStuff.startSyncLoop()
audio.tryPlayFile("./OLD/draw.mp3")
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


