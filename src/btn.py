import RPi.GPIO as GPIO

# 0 - RED, 1 - YELLOW, 2 - POWEROFF
# buttons = [3, 5, 7]

# 0 - PLAY/PAUSE, 1 - VOL MINUS, 2 - VOL PLUS
buttons = [40, 38, 36]
def initButtons():
    GPIO.setwarnings(True) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    for id in buttons:
        # GPIO.setup(id, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(id, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def getBtn(idx):
    return GPIO.input(buttons[idx]) == 0

def getBtns():
    res = []
    for id in buttons:
        res.append(GPIO.input(id))
    return res