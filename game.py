class Game:
    connection = None

    @classmethod
    def setConnection(cls, connection) -> None:
        cls.connection = connection

    def __init__(self):
        self.myTeam = {}

    async def getSession(self) -> dict:
        return await (await self.connection.request("get", "/lol-champ-select/v1/session")).json()
    
    async def updateMyTeam(self) -> None:
        session = await self.getSession()
        myTeam  = session.get("myTeam", {})
        self.myTeam = myTeam