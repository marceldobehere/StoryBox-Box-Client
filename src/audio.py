from time import sleep
import vlc
import src.files as files
import os.path
import json
import src.btn as btn

# playlist = {}
# testPlayList = {
#     "12345": "draw.mp3",
#     "874127460810": "t.mp3",
#     "338358677895": "nokia klingel.wav",
#     "682123768128": "scream.mp3",
#     "528310846334": "bruh.wav",
#     "541262328181": "fart-2.wav"
# }

playlistMap = {}
testPlaylistMap = [
    {
        "id": 541262328181,
        "name": 'Playlist 1',
        "audioFiles": [1, 2, 3]
    },
    {
        "id": 2,
        "name": 'Playlist 2',
        "audioFiles": [1, 3]
    },
    {
        "id": 528310846334,
        "name": 'Playlist RED CHIP',
        "audioFiles": [1, 2]
    },
    {
        "id": 874127460810,
        "name": 'Playlist BLUE CHIP',
        "audioFiles": [3, 1]
    },
]



def getDownloadedFiles():
    downloaded = files.getFilesInFolder("audios")
    print(downloaded)
    res = []
    for filename in downloaded:
        res.append(str(filename.replace("DOWNLOAD_", "").split(".")[0]))
    return res

def getAllFilesNeeded():
    res = []
    for playlist in playlistMap:
        for fileId in playlist["audioFiles"]:
            if not str(fileId) in res:
                res.append(str(fileId))

    return res


def tryPlayFile(path):
    pass

def getFilenameFromPlaylist(playlist_id):
    pass

def tryPlayPlaylist(id):
    pass

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















def getFileFromId(id):
    res = playlist.get(str(id))
    print('"' + str(id) + '" -> ' + str(res) + " " + str(playlist))
    if res == None:
        return ""
    else:
        return res

def tryPlaySound(id):
    print(' > Attempting to play from ID: ' + str(id))
    filename = getFileFromId(id)
    if filename == "":
        print(' > Unkown ID!')
        sleep(1)
        return
    print(" > Playing: " + filename)

    player = vlc.MediaPlayer("./test_audio/"+filename)
    player.audio_set_volume(100)
    
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
        sleep(0.1)

    print('  > Stop')
    player.stop()
