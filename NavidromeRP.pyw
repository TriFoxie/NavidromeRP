from requests import get as htget
from time import sleep
from pypresence import Presence, ActivityType, StatusDisplayType
import json

def getPlayerData(server, username, password):
    response = htget(server + "/rest/getNowPlaying.view?u=" + username + "&p=" + password + "&v=1.13.0&c=nrp&f=json")
    data = response.json()

    for player in data["subsonic-response"]["nowPlaying"]["entry"]:
        if player["username"] == username:
            return player

    return None

def refreshRPC(data):
    print("Refreshing RPC...")

    title = data["title"]
    artist = data["artists"][0]["name"]
    album = data["album"]
    year = str(data["year"])

    RPC.update(
        activity_type=ActivityType.LISTENING,
        status_display_type=StatusDisplayType.STATE,
        state=artist,
        details=title,
        large_image='navidromerp',
        large_text=album + " - " + year
    )

#load auth settings
auth = json.loads(open("auth.json").read())

#connect RPC
RPC = Presence(auth["discord_token"])
RPC.connect()

#refresh RPC
while True:
    refreshRPC(getPlayerData(auth["server"], auth["username"], auth["password"]))
    sleep(10)