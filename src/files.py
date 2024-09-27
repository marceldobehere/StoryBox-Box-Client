import os
import os.path

def readFile(path):
    f = open(path, "r")
    return f.read()

def writeFile(path, text):
    f = open(path, "w")
    f.write(text)
    f.close()

def readFileOrDef(path, defaultText):
    if not os.path.isfile(path):
        writeFile(path, defaultText)
    return readFile(path)