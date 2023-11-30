from logger     import Logger
from options    import Options

class Chat:
    connection  = None
    logger      = Logger("Chat")
    options     = Options()

    @classmethod
    def setConnection(cls, connection) -> None:
        cls.connection = connection

    def __init__(self):
        self.canChat = False
    
    async def GetRoomID(self) -> str:
        data = await (await self.connection.request('get', '/lol-chat/v1/conversations')).json()
        roomData = {}
        for i in data:
            if i['type'] == 'championSelect':
                roomData = i
                break
        return roomData['id']

    async def SendMessage(self, message: str, type: str ="chat") -> None:
        if not (await self.options.getOption("SubFeature", "SendMessage")):
            return
        try:
            roomID = await self.GetRoomID()
            messageDataBody = {
                "body": message,
                "type": type,
            }
            await self.connection.request('post', '/lol-chat/v1/conversations/' + roomID + '/messages', data=messageDataBody)
        except Exception as e:
            self.logger.log.error(e)

    async def GetMe(self):
       data = await (await self.connection.request('get', '/lol-chat/v1/me')).json()
       return data
    
    async def processMessage(self, connection, event):
        lastMessage = event.data
        
        if not "body" in lastMessage:
            return
    
        body    = lastMessage["body"]
        type    = lastMessage["type"]
        owner   = lastMessage["fromSummonerId"]

        if type == "system" and body == "joined_room":
            self.canChat = True