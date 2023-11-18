class Chat:
    connection = None

    @classmethod
    def setConnection(cls, connection) -> None:
        cls.connection = connection
    
    async def GetRoomID(self) -> str:
        data = await (await self.connection.request('get', '/lol-chat/v1/conversations')).json()
        roomData = {}
        for i in data:
            if i['type'] == 'championSelect':
                roomData = i
                break
        return roomData['id']

    async def SendMessage(self, message: str, type: str ="chat") -> None:
        try:
            roomID = await self.GetRoomID()
            messageDataBody = {
                "body": message,
                "type": type,
            }
            await self.connection.request('post', '/lol-chat/v1/conversations/' + roomID + '/messages', data=messageDataBody)
        except Exception as e:
            print(e)