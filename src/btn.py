import RPi.GPIO as GPIO

# 0 - RED, 1 - YELLOW, 2 - POWEROFF
buttons = [3, 5, 7]
def initButtons():
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    for id in buttons:
        GPIO.setup(id, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def getBtn(idx):
    return GPIO.input(buttons[idx]) == 0