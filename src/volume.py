from time import sleep
import src.btn as btn
box_volume = 50

def init_volume():
    global box_volume
    box_volume = 50
    print("> Updating Box Volume to: ", box_volume)

def increase_volume():
    global box_volume
    box_volume += 5
    if box_volume > 100:
        box_volume = 100
    print("> Updating Box Volume to: ", box_volume)

def decrease_volume():
    global box_volume
    box_volume -= 5
    if box_volume < 0:
        box_volume = 0
    print("> Updating Box Volume to: ", box_volume)

def volume_btn_check():
    if btn.getBtn(1):
        sleep(0.1)
        decrease_volume()
        return True

    if btn.getBtn(2):
        sleep(0.1)
        increase_volume()
        return True

    return False
        