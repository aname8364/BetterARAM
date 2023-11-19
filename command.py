from data_dragon import DataDragonAPI
from chat import Chat
from summoner import Summoner
from game import Game

class Command:
    commands = {}

    @classmethod
    def initCommands(cls) -> None:
        cls.commands = {
            "t"     : cls.cmdTest,
            "딥롤"  : cls.cmdDeepLol,
            "나"    : cls.cmdDeepLolSolo
        }

    def __init__(self) -> None:
        self.game        = Game()
        self.chat        = Chat()
        self.summoner    = Summoner()
        self.api         = DataDragonAPI()

    async def setOwner(self, ownerId) -> None:
        self.owner = ownerId

    async def cmdTest(self, prefix: str = "", text: str = "", *args) -> None:
        print("cmdTest executed")
        await self.chat.SendMessage(f"message\nprefix: {prefix}\ntext: {text}")

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
            championName = await self.api.findChampionFromKey(championId)
        
            if summonerName == "" or not championName:
                continue
        
            message += f"{summonerName}: https://www.deeplol.gg/champions/{championName.lower()}/build/aram\n"
        await self.chat.SendMessage(message)

    async def cmdDeepLolSolo(self, *args) -> None:
        print("cmdDeepLolSolo executed")
        await self.game.updateMyTeam()

        for teamMate in self.game.myTeam:
            summonerId: int = teamMate.get("summonerId", -1)
            championId: int = teamMate.get("championId", -1)
            
            if summonerId == -1 or championId == -1:
                continue

            if summonerId != self.owner:
                continue

            summonerName = (await self.summoner.GetSummonerWithId(summonerId)).get("displayName", "")
            championName = await self.api.findChampionFromKey(championId)

            if summonerName == "" or not championName:
                continue

            message = f"{summonerName}: https://www.deeplol.gg/champions/{championName.lower()}/build/aram\n"
        await self.chat.SendMessage(message)
        

    async def connect(self, connection) -> None:
        Game.setConnection(connection)
        Chat.setConnection(connection)
        Summoner.setConnection(connection)

    async def processMessage(self, connection, event) -> None:
        lastMessage = event.data

        body    = lastMessage["body"]
        type    = lastMessage["type"]
        owner   = lastMessage["fromSummonerId"]

        await self.setOwner(owner)

        command, *parameters = body.split()
        command = command[1:]

        if command in self.commands:
            await self.commands[command](self, *parameters)