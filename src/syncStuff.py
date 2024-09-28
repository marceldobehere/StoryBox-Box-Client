import threading
import src.network as network
import src.audio as audio
import src.network as network
import src.files as files
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
            files.removeFile("./audios/DOWNLOAD_"+str(file)+".mp3")
        except Exception as error:
            print("  > Error during deletion: ", error)





# does a ping every 10 minutes
def my_function():
    network.doPing()

def run_function():
    thread = threading.Timer(10 * 60.0, run_function)
    thread.start()
    my_function()

def do_something():
    run_function() # start the timer