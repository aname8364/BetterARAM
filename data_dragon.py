import aiohttp
import asyncio
from typing import Optional, Dict

class DataDragonAPI:
    BASE_URL        = "https://ddragon.leagueoflegends.com"
    gameVersion     = ""
    championData    = {}
    championTable   = {}
    isInited        = False

    async def init(self) -> None:
        if not self.isInited:
            await self.updateVersion()
            await self.updateChampionData()
            await self.mapChampionId()
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
                    print(f"Error during HTTP request: {e}")
                    return None

    async def updateVersion(self) -> str:
        version = await self.getData("/api/versions.json")
        if version:
            self.gameVersion = version[0]

    async def updateChampionData(self) -> Dict:
        champion = await self.getData(f"/cdn/{self.gameVersion}/data/en_US/champion.json")
        if champion:
            championData = champion.get("data", {})
            if championData:
                self.championData = championData
            else:
                print("updateChampionData: Failed to get champion.json")
            
    async def getChampionId(self, name: str) -> Optional[str]:
        champion = self.championData.get(name, {})
        if champion:
            return champion.get("key", -1)
            
    async def mapChampionId(self):
        for championName, championData in self.championData.items():
            championId = championData.get("key", -1)
            self.championTable[int(championId)] = championName

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

    twistedFate = await api.getChampionId("TwistedFate")
    print(twistedFate)

if __name__ == "__main__":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(test())
