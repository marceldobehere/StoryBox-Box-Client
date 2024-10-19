import requests
import src.boxData as boxData
import src.audio as audio

box_server_url = "https://storybox-server-box-157863384612.us-central1.run.app"

def getTestFile(audio_id):
    try:
        url = box_server_url + '/file/' + boxData.serialCode + '/audio/' + str(audio_id)
        response = requests.get(url, timeout=4)

        print(response.status_code)
        if response.status_code != 200:
            return False
        # print(response.content)

        filename = audio.getFileNameFromId(audio_id, True)
        # filename = "./audios/DOWNLOAD_"+str(audio_id)+".mp3"
        with open(filename, "wb") as binary_file:
            binary_file.write(response.content)

        print("> File Written!")
        return True
    except Exception as error:
        print("  > Error during Get File: ", error) 
        return False


def getPlaylists():
    try:
        url = box_server_url + '/file/' + boxData.serialCode + '/playlists'
        response = requests.get(url, timeout=4)

        print(response.status_code)
        if response.status_code != 200:
            return None
        
        return response.content    
    except Exception as error:
        print("  > Error during Get Playlist: ", error) 
        return None

def doPing():
    try:
        response = requests.get("https://cdn.marceldobehere.com/file/PING_FROM_PI", timeout=4)
    except Exception as error:  
        print("  > Error during Ping: ", error) 