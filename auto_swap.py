from typing         import List
from json           import loads, dumps
from dataclasses    import dataclass
from aiofiles       import open, ospath

from game           import Game
from chat           import Chat
from data_dragon    import DataDragonAPI
from logger         import Logger
from options        import Options

@dataclass
class BenchChampion:
    championId: int
    isPriority: bool

class AutoSwap:
    connection  = None
    filePath    = "favorite_champion.json"
    logger      = Logger("AutoSwap")
    options     = Options()

    @classmethod
    def setConnection(cls, connection) -> None:
        cls.connection = connection

    def __init__(self):
        self.game   = Game()
        self.chat   = Chat()
        self.api    = DataDragonAPI()

    async def checkFilePath(self) -> None:
        if not (await ospath.isfile(self.filePath)):
            self.logger.log.debug(f"Creating {self.filePath}")
            async with open(self.filePath, mode="w") as file:
                await file.write(dumps({}))

    async def loadFavoriteChampion(self) -> None:
        await self.checkFilePath()
        async with open(self.filePath, "r", encoding="UTF-8") as file:
            content = await file.read()
        self.favChampion = loads(content)

    async def start(self) -> None:
        self.me = await self.chat.GetMe()
        await self.api.init()
        await self.loadFavoriteChampion()

    async def getBench(self) -> List[BenchChampion]:
        session     = await self.game.getSession()
        bench       = session.get("benchChampions", [])
        return bench
    
    async def getMyChampion(self) -> int:
        session     = await self.game.getSession()
        myTeam      = session.get("myTeam", [])
        myChampion  = -1
        for teamMate in myTeam:
            teamMateId  = teamMate.get("summonerId", -1)
            myId        = self.me.get("summonerId", -1)
            if teamMateId != -1 and myId != -1:
                if teamMateId == myId:
                    myChampion = teamMate.get("championId", -1)
                    break
        return myChampion

    async def getMyChampionPriority(self) -> int:
        myChampion: int = await self.getMyChampion()
        curChampionName = self.api.championTable[myChampion]
        curPriority     = -1
        for priority, champion in self.favChampion.items():
            if champion == curChampionName["local"]:
                curPriority = priority
                break
        return curPriority
    
    async def checkBench(self) -> None:
        # to do: sort champion by priority and swap champion[0]
        bench       = await self.getBench()
        if not bench:
            return
        curPriority = await self.getMyChampionPriority()
        for priority, champion in self.favChampion.items():
            for benchChampion in bench:
                favChampionId   = self.api.championTable.get(champion, -1)
                benchChampionId = benchChampion.get("championId", -1)
                if favChampionId == benchChampionId:
                    if curPriority == -1 or priority < curPriority:
                        await self.connection.request("post", f"/lol-champ-select/v1/session/bench/swap/{favChampionId}")
                        self.logger.log.info(f"Swap to {champion} (priority: {priority})")
                        if self.chat.canChat:
                            await self.chat.SendMessage((await self.options.getOption("CoreFeature", "AutoSwapMessage")).format(champion=champion, priority=priority))