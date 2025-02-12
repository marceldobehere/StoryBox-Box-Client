import subprocess
import threading
from time import sleep, time
import src.files as files
import os.path




deviceStr = "C0:DC:DA:86:E9:0B"

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


def parseBluetoothCommand(str):
    if str.endswith("^") or "\b" in str:
        return "> Cancelled Command."

    print("> Got Bluetooth command: \"" + str + "\"")


    

    return "> Yes"


def startBluetoothThread():
    thread = threading.Timer(1.0, bluetoothStuff)
    thread.start()
