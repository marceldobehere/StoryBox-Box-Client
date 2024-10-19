import asyncio
from websockets.sync.client import connect
wsServerPath = "wss://storybox-server-box-157863384612.us-central1.run.app/ws/connect"

def initWs():
    print("> Doing WS Init")
    try:
        with connect(wsServerPath) as websocket:
            message = websocket.recv()
            print(f" > Received: {message}")
            websocket.send("Hello world!")
            message = websocket.recv()
            print(f" > Received: {message}")
    except Exception as error:
        print("> WS ERROR: ", error)   