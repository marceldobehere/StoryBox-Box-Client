import src.files as files

serialCode = ""
accountCode = ""

def initBoxData():
    global serialCode, accountCode

    serialCode = files.readFileOrDef("./data/serial_code.txt", "SERIAL-12345-TEST")
    print("> Serial Code: " + serialCode)

    accountCode = files.readFileOrDef("./data/account_code.txt", "ACCOUNT-BRUH_12345-TEST")
    print("> Account Code: " + accountCode)