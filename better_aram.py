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
    VERSION         = "1.0.1"
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
        self.logger.log.info(f"Current version: {self.VERSION}")
        response = get("https://raw.githubusercontent.com/aname8364/BetterARAM/main/version")
        response.raise_for_status()

        if response.status_code == 200:
            latestVersion   = version.parse(response.text.rstrip())
            currentVersion  = version.parse(self.VERSION)

            if currentVersion == latestVersion:
                self.logger.log.info(f"You are using the latest version.")
            elif currentVersion < latestVersion:
                self.logger.log.warning(f"A new version is avaliable.")
            else:
                self.logger.log.debug("version > latestVersion")
        else:
            self.logger.log.error("Failed to check version.")
            
    async def connect(self, connection):
        log     = self.logger.log
        options = self.options
        log.info("connected")
        Chat.setConnection(connection)
        AutoSwap.setConnection(connection)
        Streak.setConnection(connection)
        await self.command.connect(connection)
        await self.api.init()
        await self.autoSwap.start()

        log.info("Started")
        while True:
            await sleep(0.5)
            phase = await (await connection.request("get", "/lol-gameflow/v1/gameflow-phase")).json()
            log.info(f"gameflow-phase: {phase}")
            if phase == "Lobby":
                pass
        
            elif phase == "Matchmaking":
                pass

            elif phase == "ReadyCheck":
                pass

            elif phase == "ChampSelect":
                if (await options.getOption("CoreFeature", "UseAutoSwap")):
                    await self.autoSwap.checkBench()
            
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
    
    async def processMessage(self, connection, event):
        lastMessage = event.data

        if not "body" in lastMessage:
            return
    
        body    = lastMessage["body"]
        type    = lastMessage["type"]
        owner   = lastMessage["fromSummonerId"]

        await self.chat.processMessage(connection, event)

        if type != "groupchat":
            return
    
        if (await self.options.getOption("CoreFeature", "UseCommand")):
            await self.command.processMessage(connection, event)

    async def phaseUpdate(self, connection, event):
        phase = event.data

        if phase == "Matchmaking":
            await self.chat.set_canChat(False)

        elif phase == "ReadyCheck":
            if (await self.options.getOption("CoreFeature", "UseAutoAccept")):
                readyCheck = await (await connection.request("get", "/lol-matchmaking/v1/ready-check")).json()
                if readyCheck["playerResponse"] == "None":
                    self.logger.log.info("Matchmaking accepted.")
                    await connection.request("post", "/lol-matchmaking/v1/ready-check/accept")
        
        elif phase == "ChampSelect":
            while not (await (self.chat.get_canChat())):
                await sleep(0.5)
            if (await self.options.getOption("CoreFeature", "UseEnterMessage")):
                await self.chat.SendMessage((await self.options.getOption("CoreFeature", "EnterMessage")))

            if (await self.options.getOption("CoreFeature", "UseStreak")):
                await self.streak.checkStreak()

            await sleep(1)

            if (await self.options.getOption("CoreFeature", "UseCommand")):
                await self.command.showHelp()

    async def disconnect(self, connection):
        await self.connector.stop()

    def start(self):
        self.logger.log.info("Starting..")
        self.checkVersion()
        self.options.start()

        @self.connector.ready
        async def connect(connection):
            await self.connect(connection)

        @self.connector.ws.register('/lol-chat/v1/conversations/', event_types=('CREATE',))
        async def processMessage(connection, event):
            await self.processMessage(connection, event)

        @self.connector.ws.register("/lol-gameflow/v1/gameflow-phase", event_types=("UPDATE",))
        async def phaseUpdate(connection, event):
            await self.phaseUpdate(connection, event)

        @self.connector.close
        async def disconnect(connection):
            await self.disconnect(connection)

        self.connector.start()


betterARAM = BetterARAM()
betterARAM.start()
