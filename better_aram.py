from asyncio    import sleep
from requests   import get

from lcu_driver import Connector
from command    import Command

def checkVersion() -> None:
    response = get("https://raw.githubusercontent.com/aname8364/BetterARAM/main/version")
    response.raise_for_status()

    if response.status_code == 200:
        latestVersion = response.text.rstrip()
        if VERSION == latestVersion:
            print("You are using the latest version.")
        elif VERSION < latestVersion:
            print(f"Current version: {VERSION}\nLatest version: {latestVersion}\nA new version is available.")
        else:
            print("???how")
    else:
        print("Failed to check version.")

print("Starting..")

Command.initCommands()

VERSION     = "0.5.1"
checkVersion()

connector   = Connector()
command     = Command()

@connector.ready
async def connect(connection):
    print("connected")
    await command.connect(connection)
    
    onceChampSelect: bool = True

    print("Started")
    while True:
        await sleep(3)
        phase = await (await connection.request("get", "/lol-gameflow/v1/gameflow-phase")).json()
        print(f"gameflow-phase: {phase}")
        if phase == "Lobby":
            pass
        
        elif phase == "Matchmaking":
            pass

        elif phase == "ReadyCheck":
            onceChampSelect = True
            pass

        elif phase == "ChampSelect":
            if onceChampSelect:
                await sleep(3)
                await command.cmdDeepLol()
                onceChampSelect = False

        elif phase == "InProgress":
            pass

        elif phase == "WaitingForStats":
            pass

        elif phase == "PreEndOfGame":
            pass

        elif phase == "EndOfGame":
            pass

        elif phase == "None":
            pass

@connector.ws.register('/lol-chat/v1/conversations/', event_types=('CREATE',))
async def processMessage(connection, event):
    lastMessage = event.data

    if not "body" in lastMessage:
        return
    
    body    = lastMessage["body"]
    type    = lastMessage["type"]
    owner   = lastMessage["fromSummonerId"]

    if type != "groupchat":
        return
    
    if body[0] == "/":
        await command.processMessage(connection, event)

@connector.close
async def disconnect(connection):
    await connector.stop()

connector.start()