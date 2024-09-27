import requests

box_server_url = "https://storybox-server-box-157863384612.us-central1.run.app"

def getTestFile(audio_id):
    url = box_server_url + '/file/audio'
    data = {"audio_id": str(audio_id)}
    response = requests.post(url, data=data)

    print(response.status_code)
    if response.status_code != 200:
        return False
    # print(response.content)


    filename = "./test_audio/DOWNLOAD_"+str(audio_id)+".mp3"
    with open(filename, "wb") as binary_file:
        binary_file.write(response.content)

    print("> File Written!")
    return True


def getPlaylists():
    pass

def doPing():
    response = requests.get("https://cdn.marceldobehere.com/file/PING_FROM_PI")