import asyncio
import json
import os
import threading
from time import sleep
import src.files as files
from websockets.sync.client import connect
import src.boxData as boxData

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
    try:
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
        print("> WS ERROR: ", error)  

# Handle a Server sent Message (e.g Delete Box)
def handleServerMsg(obj):
    print(f" WS> Received Server Obj: {obj}")

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


def boxStatusReply(obj):
    print(f" > Box Status Reply: {obj}")

def boxStatus(status, currentToyId):
    if status != "IDLE" and status != "PLAYING":
        raise Exception("INVALID STATUS")
    attachListener("box_status", boxStatusReply)
    sendData("box_status", {"status": status, "current-toy-id":currentToyId})


def deleteBoxData():
    files.removeFolder("./data")
    files.removeFolder("./audios")