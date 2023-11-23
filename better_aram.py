from requests       import get
from asyncio        import sleep
from packaging      import version

from lcu_driver     import Connector

from data_dragon    import DataDragonAPI
from command        import Command
from game           import Game
from chat           import Chat
from auto_swap      import AutoSwap
from logger         import Logger
from streak         import Streak
from options        import Options

class BetterARAM:
    VERSION         = "0.9.0"
    connector       = Connector()
    logger          = Logger("BetterARAM")
    command         = Command()
    game            = Game()
    api             = DataDragonAPI()
    chat            = Chat()
    autoSwap        = AutoSwap()
    streak          = Streak()
    options         = Options()

    def checkVersion(self) -> None:
        response = get("https://raw.githubusercontent.com/aname8364/BetterARAM/main/version")
        response.raise_for_status()

        if response.status_code == 200:
            latestVersion   = version.parse(response.text.rstrip())
            currentVersion  = version.parse(self.VERSION)
            if currentVersion == latestVersion:
                self.logger.log.info(f"Current version: {self.VERSION}\nYou are using the latest version.")
            elif currentVersion < latestVersion:
                self.logger.log.warning(f"Current version: {self.VERSION}\nLatest version: {latestVersion}\nA new version is available.")
            else:
                self.logger.log.debug("version > latestVersion")
        else:
            self.logger.log.error("Failed to check version.")

    def start(self):
        self.logger.log.info("Starting..")
        self.checkVersion()
        self.options.loadOptions()
        self.connector.start()

betterARAM  = BetterARAM()

@BetterARAM.connector.ready
async def connect(connection):
    log     = BetterARAM.logger.log
    options  = BetterARAM.options
    log.info("connected")
    Chat.setConnection(connection)
    AutoSwap.setConnection(connection)
    Streak.setConnection(connection)
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
            onceChampSelect = True
        
        elif phase == "Matchmaking":
            onceChampSelect = True

        elif phase == "ReadyCheck":
            onceChampSelect = True

        elif phase == "ChampSelect":
            if onceChampSelect:
                await sleep(4)
                enterMessage = await options.getOption("Other", "EnterMessage")
                await BetterARAM.chat.SendMessage(enterMessage)

                if (await options.getOption("CoreFeature", "UseStreak")):
                    await BetterARAM.streak.checkStreak()

                if (await options.getOption("CoreFeature", "UseCommand")):
                    await BetterARAM.command.showHelp()

                onceChampSelect = False

            if (await options.getOption("CoreFeature", "UseAutoSwap")):
                await betterARAM.autoSwap.checkBench()
            

        elif phase == "InProgress":
            pass

        elif phase == "Reconnect":
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
        if (await BetterARAM.options.getOption("CoreFeature", "UseCommand")):
            await betterARAM.command.processMessage(connection, event)

@BetterARAM.connector.close
async def disconnect(connection):
    await BetterARAM.connector.stop()


betterARAM.start()