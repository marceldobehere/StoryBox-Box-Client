from time import sleep
import src.btn as btn
import src.files as files
box_volume = 50

def saveVolume(new_volume):
    global box_volume

    if new_volume > 100:
        new_volume = 100
    if new_volume < 0:
        new_volume = 0
    
    box_volume = new_volume
    print("> Updating Box Volume to: ", box_volume)
    files.writeFile("./data/volume.txt", str(box_volume))
    
def initVolume():
    boxVolume = files.readFileOrDef("./data/volume.txt", "50")
    print("> Loaded Volume: " + boxVolume)

    volume = 50
    try:
        volume = int(boxVolume)
    except:
        pass

    saveVolume(volume)

def increaseVolume():
    global box_volume
    saveVolume(box_volume + 5)

def decreaseVolume():
    global box_volume
    saveVolume(box_volume - 5)

def volumeBtnCheck():
    if btn.getBtn(1):
        sleep(0.1)
        decreaseVolume()
        return True

    if btn.getBtn(2):
        sleep(0.1)
        increaseVolume()
        return True

    return False
        