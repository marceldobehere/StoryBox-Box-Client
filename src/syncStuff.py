import threading
import src.network as network
import src.audio as audio
import src.network as network
import src.files as files
from time import sleep
import json

def updatePlaylist():
    print (" > Updating Playlists")
    try:
        print("  > Downloading Playlists")
        tempPlaylistStr = network.getPlaylists()
        if tempPlaylistStr is None:
            return
    
        print("  > Parsing Playlists")
        tempPlaylist = json.loads(tempPlaylistStr)
        # print("  > Temp Playlist:", tempPlaylist)
        # print("  > Old Playlist:", audio.playlistMap)

        print("  > Saving Playlists...")
        audio.savePlaylistData(tempPlaylist)
        # print("  > New Playlist:", audio.playlistMap)
        print("  > Done")
    except Exception as error:
        print("  > Error during download: ", error) 

def performSync():
    try:
        print("> Performing Sync")

        updatePlaylist()

        downloaded = audio.getDownloadedFiles()
        needed = audio.getAllFilesNeeded()

        print(" > Downloaded: ", downloaded)
        print(" > Needed: ", needed)

        needToDownload = []
        for file in needed:
            if not file in downloaded:
                needToDownload.append(file)

        needToDelete = []
        for file in downloaded:
            if not file in needed:
                needToDelete.append(file)

        print(" > Need to Download:", needToDownload)
        print(" > Need to Delete: ", needToDelete)

        print(" > Downloading new Files")
        for file in needToDownload:
            try:
                print("  > Downloading File: ", file)
                if network.getTestFile(file) is None:
                    print("  > Failed to download ")
            except Exception as error:
                print("  > Error during download: ", error)

        print(" > Deleting old Files")
        for file in needToDelete:
            try:
                print("  > Deleting File: ", file)
                files.removeFile(audio.getFileNameFromId(file, True))
            except Exception as error:
                print("  > Error during deletion: ", error)

        print(" > Sync complete")
    except Exception as error:
        print("  > Error during sync: ", error) 


# does a ping + sync every 10 minutes
def my_function():
    try:
        network.doPing()
        performSync()
    except Exception as error:
        print("  > Error during sync: ", error) 

def run_function():
    thread = threading.Timer(60 * 10.0, run_function)
    thread.start()
    sleep(5)
    my_function()

def startSyncLoop():
    run_function() # start the timer