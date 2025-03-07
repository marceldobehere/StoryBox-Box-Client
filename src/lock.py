from time import sleep
import src.btn as btn
box_locked = False

def saveLock(locked):
    global box_locked
    box_locked = locked
    
    print("> Updating Box Lock to: ", box_locked)
    
def initLock():
    box_lock = False
    saveLock(box_lock)
