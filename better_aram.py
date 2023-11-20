from asyncio        import sleep
from requests       import get

from lcu_driver     import Connector

from data_dragon    import DataDragonAPI
from command        import Command
from game           import Game
from chat           import Chat
from auto_swap      import AutoSwap
from logger         import Logger

class BetterARAM:
    VERSION         = "0.7.5"
    connector       = Connector()
    logger          = Logger("BetterARAM")

    def __init__(self):
        self.command    = Command()
        self.game       = Game()
        self.api        = DataDragonAPI()
        self.chat       = Chat()
        self.autoSwap   = AutoSwap()

    def checkVersion(self) -> None:
        response = get("https://raw.githubusercontent.com/aname8364/BetterARAM/main/version")
        response.raise_for_status()

        if response.status_code == 200:
            latestVersion = response.text.rstrip()
            if self.VERSION == latestVersion:
                self.logger.log.info("You are using the latest version.")
            elif self.VERSION < latestVersion:
                self.logger.log.warning(f"Current version: {self.VERSION}\nLatest version: {latestVersion}\nA new version is available.")
            else:
                self.logger.log.debug("version > latestVersion")
        else:
            self.logger.log.error("Failed to check version.")

    def start(self):
        self.logger.log.info("Starting..")
        self.checkVersion()
        self.connector.start()

betterARAM  = BetterARAM()

@BetterARAM.connector.ready
async def connect(connection):
    log = BetterARAM.logger.log
    log.info("connected")
    Chat.setConnection(connection)
    AutoSwap.setConnection(connection)
    await betterARAM.command.connect(connection)
    await betterARAM.api.init()
    await betterARAM.autoSwap.start()
    
    onceChampSelect: bool = True

    log.info("Started")
    while True:
        await sleep(1)
        phase = await (await connection.request("get", "/lol-gameflow/v1/gameflow-phase")).json()
        log.info(f"gameflow-phase: {phase}")
        if phase == "Lobby":
            pass
        
        elif phase == "Matchmaking":
            pass

        elif phase == "ReadyCheck":
            onceChampSelect = True

        elif phase == "ChampSelect":
            if onceChampSelect:
                # streak here
                await sleep(1)
                onceChampSelect = False
            await betterARAM.autoSwap.checkBench()
            

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

@BetterARAM.connector.ws.register('/lol-chat/v1/conversations/', event_types=('CREATE',))
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
        await betterARAM.command.processMessage(connection, event)

@BetterARAM.connector.close
async def disconnect(connection):
    await BetterARAM.connector.stop()


betterARAM.start()