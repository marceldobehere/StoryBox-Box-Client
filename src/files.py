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

def getFilesInFolder(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def removeFile(path):
    if os.path.exists(path):
        os.remove(path)