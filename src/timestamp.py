
from datetime import datetime

def printTimeLog(msg):
    now = datetime.now() # current date and time

    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    print(f"[{date_time}]: {msg}")	