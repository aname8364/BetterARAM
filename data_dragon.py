import requests
from typing import Optional, Dict
import asyncio

class DataDragonAPI:
    BASE_URL = "https://ddragon.leagueoflegends.com"

    def getData(self, endPoint: str) -> Optional[Dict]:
        url = f"{self.BASE_URL}{endPoint}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.HTTPError as errh:
            print("HTTP Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Error:", err)

    def getVersion(self) -> str:
        version = self.getData("/api/versions.json")
        if version:
            return version[0]

    def getChampionData(self, version: str) -> Dict:
        champion = self.getData(f"/cdn/{version}/data/en_US/champion.json")
        if champion:
            return champion

    async def findChampionFromKey(self, championData: Dict, key: int) -> Optional[str]:
        championList = championData.get("data", {})
        for championName, championData in championList.items():
            if int(championData["key"]) == key:
                return championName

async def test():
    api = DataDragonAPI()
    try:
        version     = api.getVersion()
        print("version: ", version)

        champion    = api.getChampionData(version)
        #print("data: ", champion)

        targetKey   = 1
        targetChampion = await api.findChampionFromKey(champion, targetKey)
        if targetChampion:
            print(f"{targetKey}: {targetChampion}")
    except TypeError:
        print("Failed to retrieve data.")

if __name__ == "__main__":
    asyncio.run(test())