from requests import get as htget
from time import sleep
from pypresence import Presence, ActivityType, StatusDisplayType
from pathlib import Path
import platform
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

def createAuth(path):
    print("No login found, creating...\n")
    server = input("Server address (e.g: http://127.0.0.1:0000): ")
    username = input("Navidrome Username: ")
    password = input("Navidrome Password: ")
    discord_token = input("Discord token: ")

    jsonString = json.dumps(
    {
        "server": server,
        "username": username,
        "password": password,
        "discord_token": discord_token
        },
        indent=4
    )

    open(path, "w").write(jsonString)
    print("File saved to: " + str(path))

def getDataPath():
    os = platform.system()
    print(os)
    home = Path.home()
    
    if os == "Linux":
        p = home / ".local/share/NavidromeRP/auth.json"
        p.parent.mkdir(exist_ok=True, parents=True)
        return p
    elif os == "Windows":
        p = home / "AppData/Local/NavidromeRP/auth.json"
        p.parent.mkdir(exist_ok=True, parents=True)
        return p
    elif os == "Darwin":
        p = home / "Library/Preferences/NavidromeRP/auth.json"
        p.parent.mkdir(exist_ok=True, parents=True)
        return p

#load auth settings
authJson = getDataPath()
try:
    auth = json.loads(open(authJson).read())
except FileNotFoundError:
    createAuth(authJson)
    auth = json.loads(open(authJson).read())
print("Logging in as " + auth["username"] + "...")

#connect RPC
RPC = Presence(auth["discord_token"])
RPC.connect()

isRpcSet = True

#refresh RPC
while True:
    try:
        refreshRPC(getPlayerData(auth["server"], auth["username"], auth["password"]))
        if isRpcSet != True:
            isRpcSet = True
            print("RPC set")
    except:
        if isRpcSet:
            print("No song detected, clearing...")
            RPC.clear()
            isRpcSet = False
            print("RPC unset")
    sleep(10)

input()
