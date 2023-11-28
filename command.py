from data_dragon    import DataDragonAPI
from chat           import Chat
from summoner       import Summoner
from game           import Game
from logger         import Logger
from options        import Options

class Command:
    commands    = {}
    logger      = Logger("Command")
    options     = Options()

    def initCommands(self) -> None:
        self.commands = {
            "deeplol"   : self.cmdDeepLol,
            "me"        : self.cmdDeepLolSolo
        }
        self.count = len(self.commands)

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
        
            summonerName    = await self.summoner.GetSummonerName(summonerId)
            championName    = self.api.championTable.get(championId, "")
        
            if summonerName == "" or not championName:
                continue
        
            message += f"{summonerName} ({championName}): https://www.deeplol.gg/champions/{championName.lower()}/build/aram\n"
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

            summonerName    = await self.summoner.GetSummonerName(summonerId)
            championName    = self.api.championTable.get(championId, "")

            if summonerName == "" or not championName:
                continue

            message += f"{summonerName} ({championName}): https://www.deeplol.gg/champions/{championName.lower()}/build/aram\n"
        await self.chat.SendMessage(message)
        

    async def connect(self, connection) -> None:
        Chat.setConnection(connection)
        Game.setConnection(connection)
        Summoner.setConnection(connection)
        await self.api.init()

    async def showHelp(self) -> None:
        await self.chat.SendMessage((await self.options.getOption("CoreFeature", "CommandMessage")).format(count=self.count))

    async def processMessage(self, connection, event) -> None:
        lastMessage = event.data

        body    = lastMessage["body"]
        type    = lastMessage["type"]
        owner   = lastMessage["fromSummonerId"]

        await self.setOwner(owner)

        command, *parameters = body.split()
        command = command[1:]

        if command in self.commands:
            try:
                await self.commands[command](*parameters)
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