from time import sleep, time
import vlc
import src.files as files
import os.path
import json
import src.btn as btn
import random
import src.volume as volume
import src.ws as ws

secure_random = random.SystemRandom()

READER_REF = None

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
        # print(" > HASH: ", files.getMd5Hash("./audios/" + filename))
        hash = files.getMd5Hash("./audios/" + filename)
        id = str(filename.replace("DOWNLOAD_", "").replace("_.", ".").split(".")[0])
        res.append({"hash":hash, "id":id})
    return res

def getAllFilesNeeded():
    res = []
    for playlist in playlistMap:
        for fileId in playlist["audioFiles"]:
            if not str(fileId) in res:
                res.append(str(fileId))

    return res

AUDIO_COMMAND = None
AUDIO_COMMAND_ARG = None
# COMMANDS ["PAUSE", "RESUME", "STOP", "SKIP_TIME", "SET_TIME", "NEXT_SONG", "PREVIOUS_SONG"]

def cmdPause():
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG = None
    AUDIO_COMMAND = "PAUSE"
def cmdResume():
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG = None
    AUDIO_COMMAND = "RESUME"
def cmdStop():
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG = None
    AUDIO_COMMAND = "STOP"
def cmdSkipTime(amt):
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG = amt
    AUDIO_COMMAND = "SKIP_TIME"
def cmdSetTime(amt):
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG = amt
    AUDIO_COMMAND = "SET_TIME"
def cmdPreviousSong():
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG = None
    AUDIO_COMMAND = "PREVIOUS_SONG"
def cmdNextSong():
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG = None
    AUDIO_COMMAND = "NEXT_SONG"


def checkTag():
    if READER_REF is None:
        return False
    return (READER_REF.read_id_no_block() is not None)

def tryPlayFile(path, updateFunc):
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
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
    updateFreq = 5000 # 2.5 seconds
    lastTime = player.get_time() // updateFreq
    lastPauseTime = time()
    lastPaused = False
    AUDIO_COMMAND = None
    TAG_RESET = time() + 0.5
    
    try:
        while True:
            if player.get_state() == Ended:
                break

            if btn.getBtn(0):
                was_playing = player.is_playing()
            
                if not was_playing:
                    timeA = time()
                    while btn.getBtn(0) and time() - timeA < 0.8:
                        sleep(0.1)
                    timeDiff = time() - timeA
                    if timeDiff > 0.7:
                        print('  > Force Stop')
                        break

                if was_playing:
                    player.pause()
                else:
                    player.play()
                print(f'  > Setting Paused to {was_playing}')

                if was_playing:
                    while btn.getBtn(0):
                        sleep(0.1)

                # cmdSkipTime(-2*1000)
                sleep(0.2)
            
            if not player.is_playing():
                if time() > lastPauseTime + 2*60:
                    print("> PAUSED TOO LONG!!!")
                    break
            else:
                lastPauseTime = time()

            if AUDIO_COMMAND is not None:
                print("> Doing Audio Command: ", AUDIO_COMMAND, ", Arg: ", AUDIO_COMMAND_ARG)

                if AUDIO_COMMAND == "PREVIOUS_SONG" and player.get_time() > 6000:
                    AUDIO_COMMAND = "SET_TIME"
                    AUDIO_COMMAND_ARG = 0

                if AUDIO_COMMAND == "PAUSE":
                    player.pause()
                elif AUDIO_COMMAND == "RESUME":
                    player.play()
                elif AUDIO_COMMAND == "STOP":
                    break
                elif AUDIO_COMMAND == "SKIP_TIME":
                    length = max(1, player.get_length())
                    newPercent = (player.get_time() + AUDIO_COMMAND_ARG) / length
                    newPercent = min(newPercent, 1)
                    newPercent = max(newPercent, 0)
                    player.set_position(newPercent)
                    lastTime = (player.get_time() + updateFreq + (updateFreq - 500)) // updateFreq
                elif AUDIO_COMMAND == "SET_TIME":
                    length = max(1, player.get_length())
                    newPercent = AUDIO_COMMAND_ARG / length
                    newPercent = min(newPercent, 1)
                    newPercent = max(newPercent, 0)
                    player.set_position(newPercent)
                    lastTime = (player.get_time() + updateFreq + (updateFreq - 500)) // updateFreq
                elif AUDIO_COMMAND == "NEXT_SONG":
                    break
                elif AUDIO_COMMAND == "PREVIOUS_SONG":
                    break
                else:
                    print("> Unknown Command: ", AUDIO_COMMAND)
                
                AUDIO_COMMAND = None
                AUDIO_COMMAND_ARG = None

            if READER_REF is not None:
                TAG_HERE_NOW = checkTag()
                if TAG_HERE_NOW:
                    if time() < TAG_RESET:
                        TAG_RESET = time() + 1
                    else:
                        print("> NEW NFC TAG BWAAAA")
                        break

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
    except Exception as error:
        print('> ERROR DURING PLAYBACK: ', error)

    print('  > Stop')
    player.stop()
    while btn.getBtn(0):
        sleep(0.1)

def findPlaylist(playlist_id):
    for playlist in playlistMap:
        if str(playlist["id"]) == str(playlist_id):
            return playlist
    return None


def pickNextSong(playlist, playlist_id, forceNext):
    global playlistLastSongMap
    id = str(playlist_id)

    print(f"> Picking next song for playlist: {id}")
    print(playlist)
    next_audio_id = None
    audioIds = playlist["audioFiles"]

    if len(audioIds) == 0:
        print("> ERR: PLAYLIST HAS NO AUDIOS: ", playlist)
        return None

    if playlist["mode"] == "random" and not forceNext:
        next_audio_id = secure_random.choice(audioIds)

    elif playlist["mode"] == "sequential" or forceNext:
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

def pickPreviousSong(playlist, playlist_id):
    global playlistLastSongMap
    id = str(playlist_id)

    print(f"> Picking previous song for playlist: {id}")
    print(playlist)
    next_audio_id = None
    audioIds = playlist["audioFiles"]

    if len(audioIds) == 0:
        print("> ERR: PLAYLIST HAS NO AUDIOS: ", playlist)
        return None

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
        audioIndex -= 1
        if audioIndex >= 0:
            return audioIds[audioIndex]
        return audioIds[0]

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
    audioFileId = pickNextSong(playlist, playlistId, False)
    tryPlayPlaylist2(audioFileId, playlist, playlistId)

def tryPlayPlaylist2(audioFileId, playlist, playlistId):
    audioFile = getFileNameFromId(audioFileId, None)
    print(" > Picked: ", audioFile)

    ws.boxStatus("PLAYING", playlistId, audioFileId, 0)
    saveCurrentPlayingSong(playlistId, audioFileId)
    try:
        tryPlayFile(audioFile, updateTimestampFunc(playlistId, audioFileId))
    except Exception as error:
        print("> ERROR WHILE TRYING PLAY FILE: ", error)
    
    global AUDIO_COMMAND
    if AUDIO_COMMAND != "NEXT_SONG" and AUDIO_COMMAND != "PREVIOUS_SONG":
        ws.boxStatus("IDLE", None, None, None)

    
    if AUDIO_COMMAND == "NEXT_SONG":
        print("> NEXT SONG")
        AUDIO_COMMAND = None
        audioFileId = pickNextSong(playlist, playlistId, True)
        tryPlayPlaylist2(audioFileId, playlist, playlistId)
    elif AUDIO_COMMAND == "PREVIOUS_SONG":
        print("> PREVIOUS SONG")
        AUDIO_COMMAND = None
        audioFileId = pickPreviousSong(playlist, playlistId)
        tryPlayPlaylist2(audioFileId, playlist, playlistId)


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