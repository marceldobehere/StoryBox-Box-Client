import json
import subprocess
import threading
from time import sleep, time
import src.files as files
import os.path
from subprocess import call



deviceStr = "C0:DC:DA:86:E9:0B"

def enableInternet():
    call("sudo nmcli radio wifi on", shell=True)
    call("sudo iwlist wlan0 scan", shell=True)


def connectInternet(ssid, password):
    ssid = ssid.replace('"', '')
    ssid = ssid.replace('\'', '')
    password = password.replace('"', '')
    password = password.replace('\'', '')
    print("> Connecting to new WIFI: ", ssid)
    enableInternet()
    print("Result: ", call("sudo nmcli dev wifi connect \"" + ssid + "\" password \"" + password + "\"", shell=True))

def run_cmd(command: str):
    """ Execute shell commands and return STDOUT """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    return stdout.decode("utf-8")

def bluetoothStuff():
    print("> Starting Bluetooth Stuff")
    print(run_cmd("bluetoothctl agent on") )
    print(run_cmd("bluetoothctl default-agent") )
    print(run_cmd("timeout 10s bluetoothctl scan on") )
    print(run_cmd(f"bluetoothctl pair {deviceStr}") )
    print(run_cmd(f"bluetoothctl connect {deviceStr}") )

    print("Entering Main Scan Loop")
    exit = False
    while not exit:
        try:
            print("> Starting Listening process")
            proc = subprocess.Popen(["sudo", "rfcomm", "listend", "hic0"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print("\r> Waiting for connection")
            while not os.path.exists("/dev/rfcomm0"):
                sleep(0.5)

            print("\r> Connection established!")
            with open("/dev/rfcomm0", 'r') as f:
                with open("/dev/rfcomm0", 'w') as f2:
                    f2.write("> Story Box Ready\r\n\r\n")
                    for line in f:
                        # print("\rGot: " + line)
                        res = parseBluetoothCommand(line.rstrip())
                        f2.write(str(res) + "\r\n")
                        # f2.write("AAA " + line + "\r\n")

            sleep(1)
            proc.terminate()
        except Exception as error:
            print("> Bluetooth error: " + str(error))
        finally:
            pass
            print("> Connection closed")


def parseBluetoothCommand(data):
    if data.endswith("^") or "\b" in data:
        return "> Cancelled Command."

    print("> Got Bluetooth command: \"" + data + "\"")

    try:
        obj = json.loads(data)
        if "cmd" in obj:
            command = obj["cmd"]

            if command == "wifi-conn":
                ssid = obj["ssid"]
                password = obj["pass"]
                print("> Connecting to ", ssid, " with password: ", password)
                connectInternet(ssid, password)
                return "> Connecting to WiFi: " + str(ssid)

    except Exception as error:
        print("  > Error during text parse: ", error) 
        return "> Error during text parse: " + str(error)


    return "> Yes"


def startBluetoothThread():
    thread = threading.Timer(1.0, bluetoothStuff)
    thread.start()
