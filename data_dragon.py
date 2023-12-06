import aiohttp
import asyncio
from typing import Optional, Dict

from logger import Logger
from options import Options

class DataDragonAPI:
    BASE_URL        = "https://ddragon.leagueoflegends.com"
    gameVersion     = ""
    championData    = {}
    championTable   = {}
    isInited        = False
    logger          = Logger("DataDragonAPI")
    options         = Options()

    async def init(self) -> None:
        if not self.isInited:
            self.language = await self.options.getOption("DataDragonAPI", "Language", "en_US")
            await self.updateVersion()
            await self.updateChampionData()
            await self.mapChampionData()
            self.isInited = True

    async def getData(self, endPoint: str) -> Optional[Dict]:
        url = f"{self.BASE_URL}{endPoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                try:
                    response.raise_for_status()
                    data = await response.json()
                    return data
                except aiohttp.ClientError as e:
                    self.logger.log.error(f"Error during HTTP request: {e}")
                    return None

    async def updateVersion(self) -> str:
        version = await self.getData("/api/versions.json")
        if version:
            self.gameVersion = version[0]

    async def updateChampionData(self) -> Dict:
        champion = await self.getData(f"/cdn/{self.gameVersion}/data/{self.language}/champion.json")
        if champion:
            championData = champion.get("data", {})
            if championData:
                self.championData = championData
            else:
                self.logger.log.error("Failed to get champion.json")
            
    async def getChampionId(self, name: str) -> Optional[str]:
        champion = self.championData.get(name, {})
        if champion:
            return champion.get("key", -1)
            
    async def mapChampionData(self):
        for championRealName, championData in self.championData.items():
            championId   = int(championData.get("key", "-1"))
            championName = championData.get("name", "")
            self.championTable[championId]   = {
                "global": championRealName,
                "local" : championName
                }
            self.championTable[championName] = championId

async def test():
    api = DataDragonAPI()
    await api.init()
    try:
        print(f"version: {api.gameVersion}")

        targetKey       = 1
        targetChampion  = api.championTable[targetKey]

        if targetChampion:
            print(f"{targetKey}: {targetChampion}")
    except TypeError:
        print("Failed to retrieve data.")

    annie = await api.getChampionId("Annie")
    print(annie)

    twistedFate = api.championTable["트위스티드 페이트"]
    print(twistedFate)

if __name__ == "__main__":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(test())
