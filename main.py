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
import src.timestamp as timestamp


LOW_POWER_MODE = False
def setLowPowerMode(state):
    global LOW_POWER_MODE
    LOW_POWER_MODE = state
    print("> Set Low Power Mode To: ", LOW_POWER_MODE)

timestamp.printTimeLog("Pre init")

try:
    btn.initButtons()
    boxData.initBoxData()
    audio.initPlaylistData()
except Exception as error:
    print("ERROR DURING INIT: " + str(error))
    exit(-1)
setLowPowerMode(False)

timestamp.printTimeLog("Post init")

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
        except Exception as error:
                print("ERROR IN LOOP: " + str(error))
        finally:
            pass
    GPIO.cleanup()



timestamp.printTimeLog("Play Audio")
audio.tryPlayFile("./OLD/draw.mp3")


timestamp.printTimeLog("Start sync loop")
syncStuff.startSyncLoop()


timestamp.printTimeLog("Main loop")
mainLoop()
timestamp.printTimeLog("Exit")
exit(0)