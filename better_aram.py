from asyncio import sleep

from lcu_driver import Connector
from data_dragon import DataDragonAPI
from chat import Chat
from summoner import Summoner
from game import Game

print("Starting..")

connector   = Connector()

game        = Game()
chat        = Chat()
summoner    = Summoner()

api         = DataDragonAPI()
version     = api.getVersion()
champion    = api.getChampionData(version)

async def cmdTest(prefix: str = "", text: str = "", *args) -> None:
        print("cmdTest executed")
        await chat.SendMessage(f"message\nprefix: {prefix}\ntext: {text}")

async def cmdDeepLol() -> None:
    print("cmdDeepLol executed")
    await game.updateMyTeam()

    message = "[BetterARAM]\n"
    for teamMate in game.myTeam:
        summonerId: int = teamMate.get("summonerId", -1)
        championId: int = teamMate.get("championId", -1)
        
        if summonerId == -1 or championId == -1:
            continue
        
        summonerName = (await summoner.GetSummonerWithId(summonerId)).get("displayName", "")
        championName = await api.findChampionFromKey(champion, championId)
        
        if summonerName == "" or not championName:
            continue
        
        message += f"{summonerName}: https://www.deeplol.gg/champions/{championName.lower()}/build/aram\n"
    await chat.SendMessage(message)

commands = {
    "t": cmdTest,
    "딥롤": cmdDeepLol
}

@connector.ready
async def connect(connection):
    print("connected")
    Game.setConnection(connection)
    Chat.setConnection(connection)
    Summoner.setConnection(connection)
    
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
                await cmdDeepLol()
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
    
    body = lastMessage["body"]
    type = lastMessage["type"]

    print(f"body: {body}\ntype: {type}")

    if type != "groupchat":
        return
    
    if body[0] == "/":
        command, *parameters = body.split()
        command = command[1:]
        print(f"command {command} with parameters: {parameters}")
        if command in commands:
            await commands[command](*parameters)

@connector.close
async def disconnect(connection):
    await connector.stop()

connector.start()
