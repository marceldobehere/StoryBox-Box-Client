import json
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

def connectAccount(accountKey, serialKey):
    try:
        url = box_server_url + '/account/connect'
        print(url)
        obj = {
            "account-secret-key": accountKey,
            "serial-key": serialKey
        }
        response = requests.post(url, timeout=4, json=obj)

        print(response.status_code, response.content)
        if response.status_code != 200:
            return False
        
        responseObj = json.loads(response.content)
        if "success" in responseObj:
            return responseObj["success"]
        else:
            return False
    except Exception as error:
        print("  > Error during Validate Session: ", error) 
        return False

def validateSession(serialKey):
    try:
        url = box_server_url + '/account/validate-session/' + serialKey
        print(url)
        response = requests.get(url, timeout=4)

        print(response.status_code)
        if response.status_code != 200:
            return False
        
        responseObj = json.loads(response.content)
        if "valid" in responseObj:
            return responseObj["valid"]
        else:
            return False
    except Exception as error:
        print("  > Error during Validate Session: ", error) 
        return False