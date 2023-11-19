import aiohttp
import asyncio
from typing import Optional, Dict

class DataDragonAPI:
    BASE_URL = "https://ddragon.leagueoflegends.com"

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

    async def getVersion(self) -> str:
        version = await self.getData("/api/versions.json")
        if version:
            return version[0]

    async def getChampionData(self, version: str) -> Dict:
        champion = await self.getData(f"/cdn/{version}/data/en_US/champion.json")
        if champion:
            return champion

    async def findChampionFromKey(self, key: int) -> Optional[str]:
        version         = await self.getVersion()
        championData    = await self.getChampionData(version)
        championList    = championData.get("data", {})
        for championName, championData in championList.items():
            if int(championData["key"]) == key:
                return championName

async def test():
    api = DataDragonAPI()
    try:
        version         = await api.getVersion()
        print("version: ", version)

        targetKey       = 1
        targetChampion  = await api.findChampionFromKey(targetKey)
        if targetChampion:
            print(f"{targetKey}: {targetChampion}")
    except TypeError:
        print("Failed to retrieve data.")

if __name__ == "__main__":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(test())
