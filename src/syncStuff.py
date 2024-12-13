import threading
import src.network as network
import src.audio as audio
import src.network as network
import src.files as files
from time import sleep
import json

def convPlaylist(playlistObj):
    res = []
    for id in playlistObj:
        temp = playlistObj[id]
        resObj = {}
        resObj["id"] = int(id)
        resObj["name"] = temp["name"]

        resObj["mode"] = temp["random"]
        # TODO: FIX or be confused???
        if temp["random"] == "":
            resObj["mode"] = "sequential"
        
        # TODO: Get from Playlist response once it exists
        autoplay = False
        resObj["autoplay"] = autoplay
        if autoplay:
            resObj["mode"] = "sequential"

        resObj["audioFiles"] = temp["audio"]
        resObj["hashes"] = temp["hashes"]
        res.append(resObj)

    return res

def updatePlaylist():
    print (" > Updating Playlists")
    try:
        print("  > Downloading Playlists")
        tempPlaylistStr = network.getPlaylists()
        if tempPlaylistStr is None:
            return
    
        print("  > Parsing Playlists")
        tempPlaylist = json.loads(tempPlaylistStr)
        print("  > Temp Playlist:", tempPlaylist)
        # print("  > Old Playlist:", audio.playlistMap)
        tempPlaylist = convPlaylist(tempPlaylist)
        print("  > Temp Playlist 2:", tempPlaylist)

        print("  > Saving Playlists...")
        audio.savePlaylistData(tempPlaylist)
        # print("  > New Playlist:", audio.playlistMap)
        print("  > Done")
    except Exception as error:
        print("  > Error during download: ", error) 

def getIdsAndHashesFromPlaylist(playlist):
    print("> Getting Hashes and Ids from remote")
    songsAndIds = []
    for key in playlist:
        # print(" > BLUB: ", key)
        for i in range(len(key["audioFiles"])):
            # print("  > BLUB: ", key["audioFiles"][i], " - ", key["hashes"][i])
            songsAndIds.append({"id": key["audioFiles"][i], "hash": key["hashes"][i]})
    return songsAndIds

def compareIdsAndHashes(downloaded, remote):
    remoteIds = list(map(lambda obj: str(obj["id"]), remote))
    remoteHashes = list(map(lambda obj: obj["hash"], remote))

    res = []

    for entry in downloaded:
        # print(" > ", entry)
        if entry["id"] in remoteIds:
            idx = remoteIds.index(entry["id"])
            if remoteHashes[idx] is None:
                print(" > REMOTE HASH IS NONE!!! ", entry["hash"], remoteHashes[idx])
            elif entry["hash"] != remoteHashes[idx]:
                print(" > HASH MISMATCH!!! ", entry["hash"], remoteHashes[idx])
                continue
            else:
                # print(" > HASH MATCH!!! ", entry["hash"], remoteHashes[idx])
                pass
        else:
            print(" > ENTRY NOT FOUND!!! ", entry["id"], remoteIds)
        res.append(entry)

    return res

def performSync():
    try:
        print("> Performing Sync")

        updatePlaylist()

        downloaded = audio.getDownloadedFiles()
        # print(" > Downloaded: ", downloaded)

        remotePlaylistStuff = getIdsAndHashesFromPlaylist(audio.playlistMap)
        # print("> Remote Playlist: ", remotePlaylistStuff)

        downloaded = compareIdsAndHashes(downloaded, remotePlaylistStuff)

        downloadedIds = list(map(lambda obj: obj["id"], downloaded))
        print(" > Downloaded Ids: ", downloadedIds)
        
        needed = audio.getAllFilesNeeded()
        print(" > Needed: ", needed)

        needToDownload = []
        for file in needed:
            if not file in downloadedIds:
                needToDownload.append(file)

        needToDelete = []
        for file in downloadedIds:
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
                files.removeFile(audio.getFileNameFromId(file, None))
            except Exception as error:
                print("  > Error during deletion: ", error)

        print(" > Sync complete")
    except Exception as error:
        print("  > Error during sync: ", error) 


# does a ping + sync every 10 minutes
def syncThreadFunc():
    try:
        network.doPing()
        performSync()
    except Exception as error:
        print("  > Error during sync: ", error) 

def threadWaitLoop():
    syncThreadFunc()
    thread = threading.Timer(60 * 10.0, threadWaitLoop)
    thread.start()
    

def startSyncLoop():
    thread = threading.Timer(5.0, threadWaitLoop)
    thread.start()

def singleForceSync():
    thread = threading.Timer(1.0, syncThreadFunc)
    thread.start()