from asyncio import sleep

from lcu_driver import Connector
from data_dragon import DataDragonAPI
from chat import Chat

connector = Connector()
print("Starting")

@connector.ready
async def connect(connection):
    print("Connected")

    chat        = Chat(connection)
    api         = DataDragonAPI()
    version     = await api.getVersion()
    champion    = await api.getChampionData(version)
    
    onceChampSelect = True

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
            pass

        elif phase == "ChampSelect":
            if onceChampSelect:
                await sleep(3)
                session = await (await connection.request("get", "/lol-champ-select/v1/session")).json()
                myTeam = session.get("myTeam", {})
                message = "[BetterARAM]\n"
                for teamMate in myTeam:
                    championId      = teamMate.get("championId", {})
                    championName    = await api.findChampionFromKey(champion, championId)
                    message += f"https://www.deeplol.gg/champions/{championName.lower()}/build/aram\n"
                await chat.SendMessage(message)
                onceChampSelect = False

        elif phase == "InProgress":
            pass

        elif phase == "WaitingForStats":
            pass

        elif phase == "PreEndOfGame":
            pass

        elif phase == "EndOfGame":
            onceChampSelect = True

        elif phase == "None":
            pass

connector.start()
