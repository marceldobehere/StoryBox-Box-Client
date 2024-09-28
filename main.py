#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep


import src.files as files
import src.audio as audio
import src.btn as btn
import src.boxData as boxData
import src.network as network
import src.syncStuff as syncStuff


try:
    btn.initButtons()
    boxData.initBoxData()
    audio.initPlaylistData()
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
                audio.tryPlayPlaylist(id)
                continue
            
            if btn.getBtn(1):
                audio.tryPlaySound(12345)
                continue
                
            sleep(0.14)
        finally:
            pass
    GPIO.cleanup()


# print("File Test: " + str(network.getTestFile(2)))

syncStuff.performSync()
exit(0)

syncStuff.do_something()
audio.tryPlaySound(12345)
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


