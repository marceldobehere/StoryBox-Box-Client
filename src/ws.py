import asyncio
import json
import threading
from websockets.sync.client import connect
wsServerPath = "wss://storybox-server-box-157863384612.us-central1.run.app/ws/connect"

def initWs():
    print("> Doing WS Init")
    thread = threading.Timer(1.0, wsLoop)
    thread.start() 

def wsLoop():
    try:
        with connect(wsServerPath) as websocket:
            message = websocket.recv()
            print(f" > Received: {message}")

            websocket.send("Hello world!")

            message = websocket.recv()
            print(f" > Received: {message}")

            while True:
                message = websocket.recv()
                getData(message)
                
    except Exception as error:
        print("> WS ERROR: ", error)  

def getData(objStr):
    print(f" WS> Received: {objStr}")
    try:
        obj = json.loads(objStr)
        print(f" WS> Received Obj: {obj}")
        if not "error" in obj or not "data" in obj or not "data" in obj:
            print("MISSING DATA IN WS RESPONSE!!!")
            return
        if obj["error"]:
            print(" WS> ERROR: ", obj["data"])
            return
        if checkListener(obj):
            return
        else:
            handleServerMsg(obj)
        
    except Exception as error:
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
    objStr = json.dumps(obj)
    print("> Sending: ", objStr)


def authBoxReply(obj):
    print(f" > Box Status Reply: {obj}")

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