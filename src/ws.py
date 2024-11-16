import asyncio
import json
import os
from subprocess import call
import threading
from time import sleep
import src.files as files
from websockets.sync.client import connect
import src.boxData as boxData
import src.audio as audio

wsServerPath = "wss://storybox-server-box-157863384612.us-central1.run.app/ws/connect"

def initWs():
    print("> Doing WS Init")
    thread = threading.Timer(0, wsLoop)
    thread.start() 
    sleep(0.3)

websocketConn = None

def sendWsObj(obj):
    global websocketConn
    if websocketConn == None:
        return False
    websocketConn.send(json.dumps(obj))
    return True

def wsLoop():
    global websocketConn
    while True:
        try:
            print("> WS (RE)CONNECT: ")
            with connect(wsServerPath) as websocket:
                websocketConn = websocket

                authBox(boxData.serialCode)

                while True:
                    message = websocket.recv()
                    getData(message)        
        except Exception as error:
            print("> WS ERROR: ", error)
        websocketConn = None

def getData(objStr):
    # print(f" WS> Received: {objStr}")
    try:
        obj = json.loads(objStr)
        # print(f" WS> Received Obj: {obj}")
        if not "error" in obj or not "data" in obj or not "data" in obj:
            print("MISSING DATA IN WS RESPONSE!!!")
            return
        if obj["error"]:
            print(" WS> ERROR: ", obj["data"])
        if checkListener(obj):
            return
        else:
            handleServerMsg(obj)
        
    except Exception as error:
        print(f" WS> Received: {objStr}")
        print("> WS ERROR 2: ", error)  

# Handle a Server sent Message (e.g Delete Box)
def handleServerMsg(obj):
    print(f" WS> Received Server Obj: {obj}")
    if obj["error"]:
        return

    if obj["type"] == "delete_box":
        print(f"> DELETE BOX SENT!!!")
        sendData("delete_box", {})
        deleteBoxData()
    
    if obj["type"] == "audio_command":
        print("> Audio Command")
        try:
            data = obj["data"]
            arg = None
            if "arg" in data:
                arg = data["arg"]
            sendData("audio_command", handleAudioCommand(data["command"], arg))
        except Exception as error:
            sendWsObj({"type": "audio_command", "error": True, "data": str(error)})


listenerDict = {}

# Check if a listener has been attached and if yes, execute the func and remove it
def checkListener(obj):
    type = obj["type"]
    if type in listenerDict:
        try:
            listenerDict[type](obj)
        except Exception as error:
            print(f"> Received Obj: {obj}")
            print("> CHECK LISTENER: ", error)  
        del listenerDict[type]
        return True
    return False

# Attach a listener obj
def attachListener(type, func):
    listenerDict[type] = func

def sendData(type, data):
    obj = {
        "type": type,
        "data": data,
        "error": False
    }
    print("> Sending: ", obj)
    sendWsObj(obj)


def authBoxReply(obj):
    print(f" > Box Auth Reply: {obj}")
    if obj["error"]:
        print("> ERR: WEBSOCKET CONNECTION FAILED TO AUTHENTICATE")
        os._exit(-1)

def authBox(serialId):
    attachListener("auth_box", authBoxReply)
    sendData("auth_box", {"id": serialId})

    # Not sure if we need it
    # Maybe something like ONLINE?
    # boxStatus("IDLE", None, None)


def boxStatusReply(obj):
    print(f" > Box Status Reply: {obj}")
    if obj["error"]:
        print("> ERR: WEBSOCKET STATUS ERR: ", obj["error"])

def boxStatus(status, currentToyId, currentAudioId, timestampMs):
    if status != "IDLE" and status != "PLAYING" and status != "PAUSED":
        raise Exception("INVALID STATUS")
    attachListener("box_status", boxStatusReply)
    sendData("box_status", {
        "status": status, 
        "current-toy-id":currentToyId, 
        "current-audio-id": currentAudioId,
        "current-audio-time": timestampMs
    })


def deleteBoxData():
    files.removeFolder("./data")
    files.removeFolder("./audios")
    print("> TODO: COMMENT OUT RESTART CODE!!!!!")
    # restart()


def handleAudioCommand(command, arg):
    print(f"> Handling Audio Command {command}, arg: {arg}")

    if command == "PAUSE":
        audio.cmdPause()
    elif command == "RESUME":
        audio.cmdResume()
    elif command == "STOP":
        audio.cmdStop()
    elif command == "SKIP_TIME":
        if arg is not None:
            audio.cmdSkipTime(arg)
        else:
            raise Exception("NO SKIP TIME PROVIDED")

    return {}

def restart():
    print("> Restarting")
    print(" > Result: ", call("sudo reboot", shell=True))




# Testing Delete Box Message
def boxDeleteTest():
    handleServerMsg({"type": "delete_box", "data": {}, "error": False})

def boxCmdTest():
    handleServerMsg({"type": "audio_command", "data": {"command":"SKIP_TIME", "arg": 20000}, "error": False})

if False:
    thread = threading.Timer(5.0, boxDeleteTest)
    thread.start() 


if False:
    thread = threading.Timer(15.0, boxCmdTest)
    thread.start() 


