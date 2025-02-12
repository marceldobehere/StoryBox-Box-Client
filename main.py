#!/usr/bin/env python

import json
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep, time
from subprocess import call
from datetime import datetime, timedelta

import src.volume as volume
import src.files as files
import src.audio as audio
import src.btn as btn
import src.boxData as boxData
import src.network as network
import src.syncStuff as syncStuff
import src.timestamp as timestamp
import src.ws as ws
import src.mfrcFix as MFRC_FIX
import src.bluetooth as bluetooth

AUTO_SHUTOFF = True
LOW_POWER_MODE = False
def setLowPowerMode(state):
    global LOW_POWER_MODE
    LOW_POWER_MODE = state
    print("> Set Low Power Mode To: ", LOW_POWER_MODE)

def enableInternet():
    call("sudo nmcli radio wifi on", shell=True)
    call("sudo iwlist wlan0 scan", shell=True)

timestamp.printTimeLog("Pre init")

try:
    btn.initButtons()
    boxData.initBoxData()    
    audio.initPlaylistData()
    volume.initVolume()

    bluetooth.startBluetoothThread()

    for i in range(5):
        if network.doPing():
            break
        else:
            print("NO INTERNET")
            audio.tryPlayFile("./OLD/error.mp3", None) # NO INTERNET WARNING
            enableInternet() # Re-Enable WIFI just in case
            sleep(3)

    if boxData.requireAccConnect():
        result = network.connectAccount(boxData.accountCode, boxData.serialCode)
        print("> Connecting Account:: ", result)
        boxData.removeAccConnectionKey()
        if not result:
            print("> ERROR: ACCOUNT SECRET KEY IS NOT VALID!!!")
            exit(-1)

    if not network.validateSession(boxData.serialCode):
        print("> ERROR: BOX IS NOT VALID!!!")
        audio.tryPlayFile("./OLD/bruh.wav", None) # WARNING SOUND IF BOX IS NOT VALID / THERE IS NO INTERNET
        # ws.deleteBoxData()
        # exit(-1)
    else:
        print("> Box is valid!")

    ws.initWs()
except Exception as error:
    print("ERROR DURING INIT: " + str(error))
    exit(-1)
setLowPowerMode(False)

timestamp.printTimeLog("Post init")

def powerOff():
    print("> Shutting off")
    print(" > Result: ", call("sudo nohup shutdown", shell=True))

def connectInternet(ssid, password):
    ssid = ssid.replace('"', '')
    ssid = ssid.replace('\'', '')
    password = password.replace('"', '')
    password = password.replace('\'', '')
    print("> Connecting to new WIFI: ", ssid)
    enableInternet()
    print("Result: ", call("sudo nmcli dev wifi connect \"" + ssid + "\" password \"" + password + "\"", shell=True))

def tryParseRfidData(data):
    if data is None:
        return
    data = data.strip()
    if data == "":
        return
    print("DATA: \"", data, "\"")
    
    try:
        obj = json.loads(data)
        if "command" in obj:
            command = obj["command"]

            if command == "wifi-connect":
                ssid = obj["ssid"]
                password = obj["password"]
                print("> Connecting to ", ssid, " with password: ", password)
                connectInternet(ssid, password)

    except Exception as error:
        print("  > Error during text parse: ", error) 

def mainLoop():
    reader = SimpleMFRC522()
    audio.READER_REF = reader

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
                sleepTime = now + timedelta(minutes=3)
                powerOffTime = now + timedelta(minutes=60)
                print("> Next Sleep:", sleepTime)
                setLowPowerMode(False)
                actionDone = False
            
            if now > sleepTime:
                setLowPowerMode(True)
                # audio.tryPlayFile("./OLD/fart-2.wav", None)
                sleepTime = now + timedelta(minutes=10)
            
            if now > powerOffTime:
                if AUTO_SHUTOFF:
                    powerOff()
                powerOffTime = now + timedelta(seconds=600)



            # print('> Waiting for Chip:')
            id = reader.read_id_no_block()
            if id:
                id, text = MFRC_FIX.read_blocks(reader, 4)
                tryParseRfidData(text)
                # MFRC_FIX.write_blocks(reader, '{"command":"wifi-connect", "ssid":"wifi", "password":"pass"}', 4)
                # MFRC_FIX.write_blocks(reader, '', 4)
                actionDone = True
                audio.tryPlayPlaylist(id)
                sleep(0.5)
                continue
            
            if btn.getBtn(0):
                actionDone = True
                timeA = time()
                while btn.getBtn(0) and not time() - timeA > 5:
                    sleep(0.1)
                if time() - timeA > 5:
                    print("SHUTDOWNNNN")
                    audio.tryPlayFile("./OLD/bruh.wav", None)
                    powerOff()
                continue
            
            if volume.volumeBtnCheck():
                actionDone = True
                continue
            
            if LOW_POWER_MODE:
                sleep(1.1)
            else:
                sleep(0.1)
        except Exception as error:
            print("ERROR IN LOOP: " + str(error))
            reader = SimpleMFRC522()#
            audio.READER_REF = reader
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
audio.tryPlayFile("./OLD/draw.mp3", None)


timestamp.printTimeLog("Start sync loop")
syncStuff.startSyncLoop()


timestamp.printTimeLog("Main loop")
mainLoop()
timestamp.printTimeLog("Exit")
exit(0)
