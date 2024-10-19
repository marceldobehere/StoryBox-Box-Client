from time import sleep
import src.btn as btn
box_volume = 50

def initVolume():
    global box_volume
    box_volume = 50
    print("> Updating Box Volume to: ", box_volume)

def increaseVolume():
    global box_volume
    box_volume += 5
    if box_volume > 100:
        box_volume = 100
    print("> Updating Box Volume to: ", box_volume)

def decreaseVolume():
    global box_volume
    box_volume -= 5
    if box_volume < 0:
        box_volume = 0
    print("> Updating Box Volume to: ", box_volume)

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
        