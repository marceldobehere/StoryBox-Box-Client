import src.files as files
import os

serialCode = ""
accountCode = ""

def initBoxData():
    global serialCode, accountCode
    if not os.path.exists("data"):
        os.makedirs("data")
    
    serialCode = files.readFileOrDef("./data/serial_code.txt", "test-serial1")
    print("> Serial Code: " + serialCode)

    accountCode = files.readFileOrDef("./data/account_code.txt", "acc_test_456")
    print("> Account Code: " + accountCode)

def requireAccConnect():
    global accountCode
    if accountCode == "":
        return False
    return True

def removeAccConnectionKey():
    global accountCode
    accountCode = ""
    files.writeFile("./data/account_code.txt", accountCode)