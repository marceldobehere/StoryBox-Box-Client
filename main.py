#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep
from subprocess import call

import src.volume as volume
import src.files as files
import src.audio as audio
import src.btn as btn
import src.boxData as boxData
import src.network as network
import src.syncStuff as syncStuff
import src.timestamp as timestamp
from datetime import datetime, timedelta

AUTO_SHUTOFF = True
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
    volume.init_volume()
except Exception as error:
    print("ERROR DURING INIT: " + str(error))
    exit(-1)
setLowPowerMode(False)

timestamp.printTimeLog("Post init")

def powerOff():
    print("> Shutting off")
    print(" > Result: ", call("sudo nohup shutdown", shell=True))

def mainLoop():
    reader = SimpleMFRC522()
    print('Ready')

    exit = False
    actionDone = True
    sleepTime = None
    powerOffTime = None
    while not exit:
        try:
            now = datetime.now()
            if actionDone:
                print("> Action Done")
                sleepTime = now + timedelta(minutes=5)
                powerOffTime = now + timedelta(minutes=60)
                print("> Next Sleep:", sleepTime)
                setLowPowerMode(False)
                actionDone = False
            
            if now > sleepTime:
                setLowPowerMode(True)
                audio.tryPlayFile("./OLD/fart-2.wav")
                sleepTime = now + timedelta(seconds=200)
            
            if now > powerOffTime:
                if AUTO_SHUTOFF:
                    powerOff()
                powerOffTime = now + timedelta(seconds=600)



            # print('> Waiting for Chip:')

            id, text = reader.read_no_block()
            if id:
                actionDone = True
                audio.tryPlayPlaylist(id)
                sleep(0.5)
                continue
            
            if btn.getBtn(0):
                actionDone = True
                sleep(0.3)
                audio.tryPlayFile("./OLD/draw.mp3")
                continue
            
            if volume.volume_btn_check():
                actionDone = True
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



def testLoop():
    while True:
        btns = btn.getBtns()
        print(btns)
        sleep(0.5)


# testLoop()

timestamp.printTimeLog("Play Audio")
audio.tryPlayFile("./OLD/draw.mp3")


timestamp.printTimeLog("Start sync loop")
syncStuff.startSyncLoop()


timestamp.printTimeLog("Main loop")
mainLoop()
timestamp.printTimeLog("Exit")
exit(0)