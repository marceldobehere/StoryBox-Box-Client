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

# marcel@story-box:~/StoryBox-Box-Client $ timeout 20s bluetoothctl
# Agent registered
# [CHG] Controller D8:3A:DD:93:DC:F3 Pairable: yes
# [CHG] Device 54:92:09:40:B4:19 Connected: yes
# Request confirmation
# [agent] Confirm passkey 523775 (yes/no): yes
# [HUAWEI P30]# 
# marcel@story-box:~/StoryBox-Box-Client $ bluetoothctl pair 54:92:09:40:B4:19
# Attempting to pair with 54:92:09:40:B4:19
# bluetoothctl trust 54:92:09:40:B4:19
# Failed to pair: org.bluez.Error.AlreadyExists
# marcel@story-box:~/StoryBox-Box-Client $ bluetoothctl connect 54:92:09:40:B4:19



def letNewDeviceConnect():
    print("> Letting Devices Connect")

    process = subprocess.Popen(["stdbuf", "-oL", "-eL", "bluetoothctl", "scan", "on"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stopped = False

    def stop():
        print("> Doing STOP!")
        stopped = True
        process.terminate()
    

    thread = threading.Timer(300.0, stop)
    thread.start()

    print("> Output:")
    dev = ""
    while True:
        line = process.stdout.readline().rstrip()
        if process.poll() is not None:
            break
        if not line:
            continue   
        line = line.decode('utf-8')
        # print(" > ", line)
        if line.endswith("Connected: yes"):
            print ("  > CONNECTED!")
            dev = line
            break
    print("> Output done")
    process.kill()

    if stopped or dev == "":
        return

    colonSplit = dev.split(':')
    lastPart = colonSplit[-2] #19
    firstPart = colonSplit[0] #... [CHG] Device 54
    lastSpacePart = firstPart.split(' ')[-1] #54
    # combine all part inbetween
    # 54:92:09:40:B4:19
    macAddress = lastSpacePart + ':' + ':'.join(colonSplit[1:-2]) + ':' + lastPart.split(' ')[0]
    print("> Device: " + macAddress)
    # pair
    sleep(1.0)
    print("> Remove: ", run_cmd(f"bluetoothctl remove {macAddress}") )

    print("> Doing Scan")
    process = subprocess.Popen(["timeout", "5", "bluetoothctl", "scan", "on"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    res = process.communicate()
    print(res)

    sleep(1.0)
    print("> Trust: ", run_cmd(f"bluetoothctl trust {macAddress}") )
    sleep(1.0)
    print("> Pairing: ", run_cmd(f"bluetoothctl pair {macAddress}") )
    sleep(1.0)
    print("> Connecting: ", run_cmd(f"bluetoothctl connect {macAddress}") )
    sleep(1.0)
    
def bluetoothInit():
    print("> Starting Bluetooth Stuff")
    print(run_cmd("bluetoothctl power on") )
    print(run_cmd("bluetoothctl agent on") )
    print(run_cmd("bluetoothctl default-agent") )
    print(run_cmd("bluetoothctl discoverable on") )
    print(run_cmd("bluetoothctl pairable on") )
    # print(run_cmd("timeout 10s bluetoothctl scan on") )
    print(run_cmd(f"bluetoothctl pair {deviceStr}") )
    # print(run_cmd(f"bluetoothctl connect {deviceStr}") )

def bluetoothSearchForDevice():
    thread = threading.Timer(1.0, letNewDeviceConnect)
    thread.start()

def bluetoothStuff():
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
            if command == "bash":
                data = obj["data"]
                print(f"> Doing command: {data}")
                res = run_cmd(data)
                print(f"> Doing command: {data} -> {res}")
                return res



    except Exception as error:
        print("  > Error during text parse: ", error) 
        return "> Error during text parse: " + str(error)


    return "> Yes"


def startBluetoothThread():
    thread = threading.Timer(1.0, bluetoothStuff)
    thread.start()
