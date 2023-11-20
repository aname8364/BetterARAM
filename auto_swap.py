from typing         import List
from json           import loads
from dataclasses    import dataclass

from game           import Game
from chat           import Chat
from data_dragon    import DataDragonAPI
from logger         import Logger

@dataclass
class BenchChampion:
    championId: int
    isPriority: bool

class AutoSwap:
    connection  = None
    filePath    = "favorite_champion.json"
    logger      = Logger("AutoSwap")

    @classmethod
    def setConnection(cls, connection) -> None:
        cls.connection = connection

    def __init__(self):
        self.game   = Game()
        self.chat   = Chat()
        self.api    = DataDragonAPI()

    async def start(self) -> None:
        self.me = await self.chat.GetMe()
        await self.api.init()
        with open(self.filePath, "r") as file:
            content = file.read()
        self.favChampion    = loads(content)

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
        myChampion      = await self.getMyChampion()
        curChampionName = self.api.championTable.get(myChampion, "")
        curPriority     = -1
        for priority, champion in self.favChampion.items():
            if champion == curChampionName:
                curPriority = priority
                break
        return curPriority
    
    async def checkBench(self) -> None:
        bench       = await self.getBench()
        curPriority = await self.getMyChampionPriority()
        for priority, champion in self.favChampion.items():
            for benchChampion in bench:
                favChampionId   = await self.api.getChampionId(champion)
                benchChampionId = benchChampion.get("championId", -1)
                if int(favChampionId) == benchChampionId:
                    self.logger.log.info(f"found favorite champion with priority {priority} from bench")
                    if curPriority == -1 or priority < curPriority:
                        await self.connection.request("post", f"/lol-champ-select/v1/session/bench/swap/{favChampionId}")
                        await self.chat.SendMessage(f"[AutoSwap] swap to {champion} (priority: {priority})")