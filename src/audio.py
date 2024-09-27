from time import sleep
import vlc
import src.files as files
import os.path
import json
import src.btn as btn

playlist = {}
testPlayList = {
    "12345": "draw.mp3",
    "874127460810": "t.mp3",
    "338358677895": "nokia klingel.wav",
    "682123768128": "scream.mp3",
    "528310846334": "bruh.wav",
    "541262328181": "fart-2.wav"
}

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

def initPlaylistData():
    global playlist
    playlistStr = files.readFileOrDef("./data/song_map.json", json.dumps(testPlayList, indent=4))
    playlist = json.loads(playlistStr)
    print("> Playlist: " + json.dumps(playlist))