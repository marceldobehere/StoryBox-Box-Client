import os
import os.path
from pathlib import Path
import shutil

def readFile(path):
    f = open(path, "r")
    return f.read()

def writeFile(path, text):
    f = open(path, "w")
    f.write(text)
    f.close()

def fileExists(path):
    return os.path.isfile(path)

def readFileOrDef(path, defaultText):
    if not os.path.isfile(path):
        writeFile(path, defaultText)
    return readFile(path)

def getFilesInFolder(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def removeFile(path):
    if os.path.exists(path):
        os.remove(path)

def removeFolder(path):
    dirpath = Path(path)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath)

def findFilenameThatStartsWith(folderPath, filenameStart):
    files = getFilesInFolder(folderPath)
    for file in files:
        if file.startswith(filenameStart):
            return file
    return None 