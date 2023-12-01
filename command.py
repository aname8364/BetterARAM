from json           import dump, load

from data_dragon    import DataDragonAPI
from chat           import Chat
from summoner       import Summoner
from game           import Game
from logger         import Logger
from options        import Options

class Command:
    runePath    = "rune.json"

    commands    = {}
    logger      = Logger("Command")
    options     = Options()

    def getPublicCount(self) -> int:
        count = 0
        for _, data in self.commands.items():
            if data["private"] is False:
                count += 1
        return count

    def initCommands(self) -> None:
        self.commands = {
            "team"      : {"private": False,    "func": self.cmdDeepLol},
            "me"        : {"private": False,    "func": self.cmdDeepLolSolo},
            "setrune"   : {"private": True,     "func": self.cmdSetRune},
            "getrune"   : {"private": True,     "func": self.cmdGetRune},
            "runes"     : {"private": True,     "func": self.cmdRunes}
        }
        self.count = self.getPublicCount()

    def __init__(self) -> None:
        self.game        = Game()
        self.chat        = Chat()
        self.summoner    = Summoner()
        self.api         = DataDragonAPI()
        self.initCommands()

    async def setOwner(self, ownerId) -> None:
        self.owner = ownerId

    async def cmdDeepLol(self, *args) -> None:
        self.logger.log.debug("cmdDeepLol executed")
        await self.game.updateMyTeam()

        message = "[DeepLOL 전체챔피언분석]\n"
        for teamMate in self.game.myTeam:
            summonerId: int = teamMate.get("summonerId", -1)
            championId: int = teamMate.get("championId", -1)
        
            if summonerId == -1 or championId == -1:
                continue
        
            summonerName        = await self.summoner.GetSummonerName(summonerId)
            championData        = self.api.championTable[championId]
            championLocalName   = championData["local"]
            championGlobalName  = championData["global"]
        
            if summonerName == "" or not championLocalName or not championGlobalName:
                continue
        
            message += f"{summonerName} ({championLocalName}): https://www.deeplol.gg/champions/{championGlobalName.lower()}/build/aram\n"
        await self.chat.SendMessage(message)

    async def cmdDeepLolSolo(self, *args) -> None:
        self.logger.log.debug("cmdDeepLolSolo executed")
        await self.game.updateMyTeam()

        message = "[DeepLOL 개인챔피언분석]\n"
        for teamMate in self.game.myTeam:
            summonerId: int = teamMate.get("summonerId", -1)
            championId: int = teamMate.get("championId", -1)
            
            if summonerId == -1 or championId == -1:
                continue

            if summonerId != self.owner:
                continue

            summonerName        = await self.summoner.GetSummonerName(summonerId)
            championData        = self.api.championTable[championId]
            championLocalName   = championData["local"]
            championGlobalName  = championData["global"]

            if summonerName == "" or not championLocalName or not championGlobalName:
                continue

            message += f"{summonerName} ({championLocalName}): https://www.deeplol.gg/champions/{championGlobalName.lower()}/build/aram\n"
        await self.chat.SendMessage(message)

    async def cmdSetRune(self, runeName, *args) -> None:
        rune = self.runeData.get(runeName, {})
        if not rune:
            self.logger.log.warning(f"No rune named {runeName} found in {self.runePath}.")
            return
        
        currentPage = await (await self.connection.request("get", "/lol-perks/v1/currentpage")).json()
        currentPageId = currentPage["id"]

        await self.connection.request("put", f"/lol-perks/v1/pages/{currentPageId}", data=rune)
        await self.connection.request("put", "/lol-perks/v1/currentpage")
        self.logger.log.info(f"Changed rune to {runeName}!")

    async def cmdGetRune(self, *args) -> None:
        currentPage = await (await self.connection.request("get", "/lol-perks/v1/currentpage")).json()
        self.logger.log.info(f"\"primaryStyleId\": {currentPage['primaryStyleId']}")
        self.logger.log.info(f"\"subStyleId\": {currentPage['subStyleId']}")
        perks = ""
        for perk in currentPage["selectedPerkIds"]:
            perks += str(perk) + " "
        self.logger.log.info(perks)

    async def cmdRunes(self, *args) -> None:
        runes = ""
        for name in self.runeData:
            runes += name + " "
        #await self.chat.SendMessage(runes)
        self.logger.log.info(runes)

    async def updateRuneData(self) -> None:
        with open(self.runePath, "r", encoding="UTF-8") as file:
            self.runeData = load(file)
        
    async def connect(self, connection) -> None:
        self.connection = connection
        Chat.setConnection(connection)
        Game.setConnection(connection)
        Summoner.setConnection(connection)
        await self.api.init()
        await self.updateRuneData()

    async def showHelp(self) -> None:
        await self.chat.SendMessage((await self.options.getOption("CoreFeature", "CommandMessage")).format(count=self.count))

    async def processMessage(self, connection, event) -> None:
        lastMessage = event.data

        body    = lastMessage["body"]
        type    = lastMessage["type"]
        owner   = lastMessage["fromSummonerId"]

        if body[0] == "/":
            await self.setOwner(owner)

            command, *parameters = body.split()
            command = command[1:]

            if command in self.commands:
                try:
                    commandData = self.commands[command]
                    commandFunc = commandData["func"]
                    private     = commandData["private"]
                    mySummerId  = (await self.chat.GetMe())["summonerId"]
                    if private and self.owner != mySummerId:
                        return
                    await commandFunc(*parameters)
                except:
                    self.logger.log.error(f"Failed to run command {command} with args {parameters}")

if __name__ == "__main__":
    from lcu_driver import Connector

    connector   = Connector()
    command     = Command()

    @connector.ready
    async def connect(connection):
        await command.connect(connection)

    @connector.ws.register('/lol-chat/v1/conversations/', event_types=('CREATE',))
    async def processMessage(connection, event):
        lastMessage = event.data

        if not "body" in lastMessage:
            return
    
        body    = lastMessage["body"]
        type    = lastMessage["type"]

        if type != "groupchat":
            return
    
        if body[0] == "/":
            await command.processMessage(connection, event)

    connector.start()