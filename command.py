from data_dragon import DataDragonAPI
from chat import Chat
from summoner import Summoner
from game import Game

class Command:
    commands = {}

    def initCommands(self) -> None:
        self.commands = {
            "deeplol"   : self.cmdDeepLol,
            "me"        : self.cmdDeepLolSolo
        }

    def __init__(self) -> None:
        self.game        = Game()
        self.chat        = Chat()
        self.summoner    = Summoner()
        self.api         = DataDragonAPI()
        self.initCommands()

    async def setOwner(self, ownerId) -> None:
        self.owner = ownerId

    async def cmdDeepLol(self, *args) -> None:
        print("cmdDeepLol executed")
        await self.game.updateMyTeam()

        message = "[BetterARAM]\n"
        for teamMate in self.game.myTeam:
            summonerId: int = teamMate.get("summonerId", -1)
            championId: int = teamMate.get("championId", -1)
        
            if summonerId == -1 or championId == -1:
                continue
        
            summonerName = (await self.summoner.GetSummonerWithId(summonerId)).get("displayName", "")
            championName = self.api.championTable.get(championId, "")
        
            if summonerName == "" or not championName:
                continue
        
            message += f"{summonerName} ({championName}): https://www.deeplol.gg/champions/{championName.lower()}/build/aram\n"
        await self.chat.SendMessage(message)

    async def cmdDeepLolSolo(self, *args) -> None:
        print("cmdDeepLolSolo executed")
        await self.game.updateMyTeam()

        message = ""
        for teamMate in self.game.myTeam:
            summonerId: int = teamMate.get("summonerId", -1)
            championId: int = teamMate.get("championId", -1)
            
            if summonerId == -1 or championId == -1:
                continue

            if summonerId != self.owner:
                continue

            summonerName = (await self.summoner.GetSummonerWithId(summonerId)).get("displayName", "")
            championName = self.api.championTable.get(championId, "")

            if summonerName == "" or not championName:
                continue

            message = f"{summonerName} ({championName}): https://www.deeplol.gg/champions/{championName.lower()}/build/aram\n"
        await self.chat.SendMessage(message)
        

    async def connect(self, connection) -> None:
        Game.setConnection(connection)
        Summoner.setConnection(connection)
        await self.api.init()

    async def processMessage(self, connection, event) -> None:
        lastMessage = event.data

        body    = lastMessage["body"]
        type    = lastMessage["type"]
        owner   = lastMessage["fromSummonerId"]

        await self.setOwner(owner)

        command, *parameters = body.split()
        command = command[1:]

        if command in self.commands:
            await self.commands[command](*parameters)