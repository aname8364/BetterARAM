class Game:
    connection  = None
    session     = {}
    myTeam      = {}

    @classmethod
    def setConnection(cls, connection) -> None:
        cls.connection = connection

    async def updateSession(self):
        self.session = await (await self.connection.request("get", "/lol-champ-select/v1/session")).json()
    
    async def updateMyTeam(self) -> None:
        session = await self.getSession()
        myTeam  = session.get("myTeam", {})
        self.myTeam = myTeam

    async def getSession(self) -> dict:
        await self.updateSession()
        return self.session