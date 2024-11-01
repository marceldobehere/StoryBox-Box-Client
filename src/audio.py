from time import sleep
import vlc
import src.files as files
import os.path
import json
import src.btn as btn
import random
import src.volume as volume
secure_random = random.SystemRandom()

playlistMap = {}
testPlaylistMap = [
    {
        "id": 541262328181,
        "name": 'Playlist 1',
        "randomPlay": 1,
        "audioFiles": [1, 2, 3]
    },
    {
        "id": 2,
        "name": 'Playlist 2',
        "randomPlay": 0,
        "audioFiles": [1, 3]
    },
    {
        "id": 528310846334,
        "name": 'Playlist RED CHIP',
        "randomPlay": 1,
        "audioFiles": [1, 2]
    },
    {
        "id": 874127460810,
        "name": 'Playlist BLUE CHIP',
        "randomPlay": 1,
        "audioFiles": [3, 1]
    },
]

# potential ending doesnt include . (e.b just "mp3")
def getFileNameFromId(id, potentialEnding):    
    filename = "DOWNLOAD_" + str(id) + "_"

    if potentialEnding != None:
        filename += "." + potentialEnding
    else:
        foundName = files.findFilenameThatStartsWith("./audios/", filename)
        # print(f"> Found Filename: \"{foundName}\"")
        if foundName == None:
            print(f"> ERR: No File found for file id: {id}")
            return ""
        filename = foundName

    return "./audios/" + filename

def getDownloadedFiles():
    downloaded = files.getFilesInFolder("audios")
    print(downloaded)
    res = []
    for filename in downloaded:
        res.append(str(filename.replace("DOWNLOAD_", "").replace("_.", ".").split(".")[0]))
    return res

def getAllFilesNeeded():
    res = []
    for playlist in playlistMap:
        for fileId in playlist["audioFiles"]:
            if not str(fileId) in res:
                res.append(str(fileId))

    return res


def tryPlayFile(path):
    if path == "" or not files.fileExists(path):
        print(' > Unkown Path! ', path)
        sleep(1)
        return
    print(" > Playing: " + path)

    player = vlc.MediaPlayer(path)
    player.audio_set_volume(volume.box_volume)
    
    print('  > Play')
    player.play()
    
    print('  > Wait')
    Ended = 6
    while True:
        if player.get_state() == Ended:
            break
        if btn.getBtn(0):
            print('  > Force Stop')
            break
        volume.volumeBtnCheck()
        player.audio_set_volume(volume.box_volume)
        sleep(0.1)

    print('  > Stop')
    player.stop()
    while btn.getBtn(0):
        sleep(0.1)

def findPlaylist(playlist_id):
    for playlist in playlistMap:
        if str(playlist["id"]) == str(playlist_id):
            return playlist

def tryPlayPlaylist(id):
    print(' > Attempting to play random song from Playlist with ID: ' + str(id))
    playlist = findPlaylist(str(id))
    if playlist is None:
        print(" > Playlist not found!")
        sleep(0.5)
        return
    print(playlist)
    audioFiles = playlist["audioFiles"]
    audioFile = secure_random.choice(audioFiles)
    audioFile = getFileNameFromId(audioFile, None)
    print(" > Picked: ", audioFile)
    tryPlayFile(audioFile)


def initPlaylistData():
    global playlistMap
    if not os.path.exists("audios"):
        os.makedirs("audios")

    playlistStr = files.readFileOrDef("./data/song_map.json", json.dumps(testPlaylistMap, indent=4))
    playlistMap = json.loads(playlistStr)
    # print("> Playlist: " + json.dumps(playlistMap))


def savePlaylistData(new_playlists):
    global playlistMap
    playlistMap = new_playlists
    files.writeFile("./data/song_map.json", json.dumps(playlistMap, indent=4))