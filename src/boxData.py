import src.files as files
import os

serialCode = ""
accountCode = ""

def initBoxData():
    global serialCode, accountCode
    if not os.path.exists("data"):
        os.makedirs("data")
    
    serialCode = files.readFileOrDef("./data/serial_code.txt", "box_serial_123")
    print("> Serial Code: " + serialCode)

    accountCode = files.readFileOrDef("./data/account_code.txt", "acc_test_456")
    print("> Account Code: " + accountCode)