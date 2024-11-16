from time import sleep
import vlc
import src.files as files
import os.path
import json
import src.btn as btn
import random
import src.volume as volume
import src.ws as ws

secure_random = random.SystemRandom()

playlistMap = {}
playlistLastSongMap = {}
testPlaylistMap = [
    {
        "id": 541262328181,
        "name": 'Playlist 1',
        "mode": "random",
        "audioFiles": [1, 2, 3]
    },
    {
        "id": 2,
        "name": 'Playlist 2',
        "mode": "random",
        "audioFiles": [1, 3]
    },
    {
        "id": 528310846334,
        "name": 'Playlist RED CHIP',
        "mode": "sequential",
        "audioFiles": [1, 2]
    },
    {
        "id": 874127460810,
        "name": 'Playlist BLUE CHIP',
        "mode": "sequential",
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


def tryPlayFile(path, updateFunc):
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
    updateFreq = 2000 # 2 seconds
    lastTime = player.get_time() // updateFreq
    lastPaused = False
    while True:
        if player.get_state() == Ended:
            break

        if btn.getBtn(0):
            # print('  > Force Stop')
            # break
            if player.is_playing():
                player.pause()
            else:
                player.play()
            print(f'  > Setting Paused to {player.is_playing()}')
            sleep(0.2)


        if updateFunc is not None:
            localLastTime = player.get_time() // updateFreq
            localPaused = not player.is_playing()
            sendUpdate = False

            if localLastTime > lastTime:
                lastTime = localLastTime
                sendUpdate = True
            if localPaused != lastPaused:
                lastPaused = localPaused
                sendUpdate = True

            if sendUpdate:
                updateFunc(player.get_time(), localPaused)

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
    return None


def pickNextSong(playlist, playlist_id):
    global playlistLastSongMap
    id = str(playlist_id)

    print(f"> Picking next song for playlist: {id}")
    print(playlist)
    next_audio_id = None
    audioIds = playlist["audioFiles"]

    if len(audioIds) == 0:
        print("> ERR: PLAYLIST HAS NO AUDIOS: ", playlist)
        return None

    if playlist["mode"] == "random":
        next_audio_id = secure_random.choice(audioIds)

    elif playlist["mode"] == "sequential":
        last_song = None
        last_song_id = None
        id = str(playlist_id)
        if id in playlistLastSongMap:
            last_song = playlistLastSongMap[id]
            last_song_id = last_song["audio_id"]
            if not last_song_id in audioIds:
                last_song_id = None
        print(f" > Last Song: ", last_song)

        if last_song_id == None:
            return audioIds[0]
        else:
            audioIndex = audioIds.index(last_song_id)
            audioIndex = (audioIndex + 1) % len(audioIds)
            return audioIds[audioIndex]

    else:
        print("> ERR: UNKOWN PLAYLIST MODE: ", playlist["mode"])
        return None

    return next_audio_id


def updateTimestamp(toyId, audioId, timeMs, paused):
    print(f"> New Timestamp: {timeMs}ms, (Paused: {paused}, Toy: {toyId}, Audio: {audioId})")
    if paused:
        ws.boxStatus("PAUSED", toyId, audioId, timeMs)
    else:
        ws.boxStatus("PLAYING", toyId, audioId, timeMs)

def updateTimestampFunc(toyId, audioId):
    return lambda timeMs, paused : updateTimestamp(toyId, audioId, timeMs, paused)

def tryPlayPlaylist(playlistId):
    print(' > Attempting to play random song from Playlist with ID: ' + str(playlistId))
    playlist = findPlaylist(str(playlistId))
    if playlist is None:
        print(" > Playlist not found!")
        sleep(0.5)
        return
    print(playlist)
    audioFileId = pickNextSong(playlist, playlistId)
    audioFile = getFileNameFromId(audioFileId, None)
    print(" > Picked: ", audioFile)

    ws.boxStatus("PLAYING", playlistId, audioFileId, 0)
    saveCurrentPlayingSong(playlistId, audioFileId)
    tryPlayFile(audioFile, updateTimestampFunc(playlistId, audioFileId))
    ws.boxStatus("IDLE", None, None, None)


def initPlaylistData():
    global playlistMap, playlistLastSongMap
    if not os.path.exists("audios"):
        os.makedirs("audios")

    # playlistStr = files.readFileOrDef("./data/song_map.json", json.dumps(testPlaylistMap, indent=4))
    playlistStr = files.readFileOrDef("./data/song_map.json", "[]")
    playlistMap = json.loads(playlistStr)
    # print("> Playlist: " + json.dumps(playlistMap))

    playlistLastSongStr = files.readFileOrDef("./data/last_song_map.json", "{}")
    playlistLastSongMap = json.loads(playlistLastSongStr)


def savePlaylistData(new_playlists):
    global playlistMap
    playlistMap = new_playlists
    files.writeFile("./data/song_map.json", json.dumps(playlistMap, indent=4))

def savePlaylistLastSong(new_lastsong):
    global playlistLastSongMap
    playlistLastSongMap = new_lastsong
    files.writeFile("./data/last_song_map.json", json.dumps(playlistLastSongMap, indent=4))

def saveCurrentPlayingSong(playlist_id, audio_id):
    global playlistLastSongMap
    playlistLastSongMap[str(playlist_id)] = {
        "audio_id": audio_id
    }
    savePlaylistLastSong(playlistLastSongMap)