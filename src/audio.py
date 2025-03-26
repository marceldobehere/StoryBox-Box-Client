from time import sleep, time
import vlc
import src.files as files
import os.path
import json
import src.btn as btn
import random
import src.volume as volume
import src.ws as ws
import src.lock as lock

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

AUDIO_COMMAND = []
AUDIO_COMMAND_ARG = []
# COMMANDS ["PAUSE", "RESUME", "STOP", "SKIP_TIME", "SET_TIME", "NEXT_SONG", "PREVIOUS_SONG"]

def cmdPause():
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG.append(None)
    AUDIO_COMMAND.append("PAUSE")
def cmdResume():
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG.append(None)
    AUDIO_COMMAND.append("RESUME")
def cmdStop():
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG.append(None)
    AUDIO_COMMAND.append("STOP")
def cmdSkipTime(amt):
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG.append(amt)
    AUDIO_COMMAND.append("SKIP_TIME")
def cmdSetTime(amt):
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG.append(amt)
    AUDIO_COMMAND.append("SET_TIME")
def cmdPreviousSong():
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG.append(None)
    AUDIO_COMMAND.append("PREVIOUS_SONG")
def cmdNextSong():
    global AUDIO_COMMAND, AUDIO_COMMAND_ARG
    AUDIO_COMMAND_ARG.append(None)
    AUDIO_COMMAND.append("NEXT_SONG")

def hasCmd():
    if len(AUDIO_COMMAND) > 0:
        print("Has CMD: ", len(AUDIO_COMMAND))
    return len(AUDIO_COMMAND) > 0

def getCmd():
    cmd, arg = AUDIO_COMMAND.pop(0), AUDIO_COMMAND_ARG.pop(0)
    print("GET CMD: ", AUDIO_COMMAND, cmd, arg)
    return cmd, arg


def checkTag():
    if READER_REF is None:
        return False
    return (READER_REF.read_id_no_block() is not None)

def tryPlayFile(path, updateFunc):
    if path == "" or not files.fileExists(path):
        print(' > Unkown Path! ', path)
        sleep(1)
        return
    print(" > Playing: " + path)

    player = vlc.MediaPlayer(path)
    sleep(0.1)
    player.audio_set_volume(volume.box_volume)

    sleep(0.5)
    
    print('  > Play')
    player.play()
    
    print('  > Wait')
    Ended = 6
    updateFreq = 5000 # 2.5 seconds
    lastTime = player.get_time() // updateFreq
    lastPauseTime = time()
    lastPaused = False

    TAG_RESET = time() + 0.5
    
    try:
        while True:
            if player.get_state() == Ended:
                break
            if lock.box_locked:
                while hasCmd():
                    getCmd()
                break

            if btn.getBtn(0) and updateFunc is not None:
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
                if time() > lastPauseTime + 3*60:
                    print("> PAUSED TOO LONG!!!")
                    lastPauseTime = time()
                    break
            else:
                lastPauseTime = time()

            if hasCmd():
                A_CMD, A_ARG = getCmd()
                print("> Doing Audio Command: ", A_CMD, ", Arg: ", A_ARG)

                if A_CMD == "PREVIOUS_SONG" and player.get_time() > 6000:
                    A_CMD = "SET_TIME"
                    A_ARG = 0

                if A_CMD == "PAUSE":
                    player.pause()
                elif A_CMD == "RESUME":
                    player.play()
                elif A_CMD == "STOP":
                    cmdStop()
                    break
                elif A_CMD == "SKIP_TIME":
                    length = max(1, player.get_length())
                    newPercent = (player.get_time() + A_ARG) / length
                    newPercent = min(newPercent, 1)
                    newPercent = max(newPercent, 0)
                    player.set_position(newPercent)
                    lastTime = (player.get_time() + updateFreq + (updateFreq - 500)) // updateFreq
                elif A_CMD == "SET_TIME":
                    length = max(1, player.get_length())
                    newPercent = A_ARG / length
                    newPercent = min(newPercent, 1)
                    newPercent = max(newPercent, 0)
                    player.set_position(newPercent)
                    lastTime = (player.get_time() + updateFreq + (updateFreq - 500)) // updateFreq
                elif A_CMD == "NEXT_SONG":
                    cmdNextSong()
                    break
                elif A_CMD == "PREVIOUS_SONG":
                    cmdPreviousSong()
                    break
                else:
                    print("> Unknown Command: ", A_CMD)
                
                A_CMD = None
                A_ARG = None

            if READER_REF is not None and updateFunc is not None:
                TAG_HERE_NOW = checkTag()
                if TAG_HERE_NOW:
                    if time() < TAG_RESET:
                        TAG_RESET = time() + 1
                    else:
                        print("> NEW NFC TAG BWAAAA")
                        A_CMD = "STOP"
                        break

            sendUpdate = False

            if updateFunc is not None and volume.volumeBtnCheck():
                sendUpdate = True
            player.audio_set_volume(volume.box_volume)

            if updateFunc is not None:
                localLastTime = player.get_time() // updateFreq
                localPaused = not player.is_playing()

                if localLastTime > lastTime:
                    lastTime = localLastTime
                    sendUpdate = True
                if localPaused != lastPaused:
                    lastPaused = localPaused
                    sendUpdate = True

                if sendUpdate:
                    updateFunc(player.get_time(), localPaused)

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

    elif playlist["mode"] == "sequential" or forceNext or playlist["autoplay"]:
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
        print("> ERR: UNKNOWN PLAYLIST MODE: ", playlist["mode"])
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
    while hasCmd():
        A_CMD, A_ARG = getCmd()
    tryPlayPlaylist2(audioFileId, playlist, playlistId)

def tryPlayPlaylist2(audioFileId, playlist, playlistId):
    playlist = findPlaylist(str(playlistId))
    if playlist is None:
        print(" > Playlist not found!")
        sleep(0.5)
        return

    if lock.box_locked:
        print(" > Box locked")
        ws.boxStatus("IDLE", None, None, None)
        sleep(0.5)
        return

    audioFile = getFileNameFromId(audioFileId, None)
    print(" > Picked: ", audioFile)

    ws.boxStatus("PLAYING", playlistId, audioFileId, 0)
    saveCurrentPlayingSong(playlistId, audioFileId)
    try:
        tryPlayFile(audioFile, updateTimestampFunc(playlistId, audioFileId))
    except Exception as error:
        print("> ERROR WHILE TRYING PLAY FILE: ", error)

    # check for playlist.autoplay
    
    doIdle = True
    while hasCmd():
        A_CMD, A_ARG = getCmd()

        if A_CMD == "NEXT_SONG":
            print("> NEXT SONG")
            doIdle = False
            audioFileId = pickNextSong(playlist, playlistId, True)
            tryPlayPlaylist2(audioFileId, playlist, playlistId)
            return
        elif A_CMD == "PREVIOUS_SONG":
            print("> PREVIOUS SONG")
            doIdle = False
            audioFileId = pickPreviousSong(playlist, playlistId)
            tryPlayPlaylist2(audioFileId, playlist, playlistId)
            return
        elif A_CMD == "STOP":
            print("> STOP")
            return

    if playlist["autoplay"]:
        print("> NEXT SONG AUTOPLAY")
        if audioFileId == playlist["audioFiles"][-1] and not playlist["loop"]:
            print("> NEXT SONG AUTOPLAY DONE")
            if doIdle:
                ws.boxStatus("IDLE", None, None, None)
            return
        audioFileId = pickNextSong(playlist, playlistId, True)
        tryPlayPlaylist2(audioFileId, playlist, playlistId)
        return

    if doIdle:
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