from typing import Optional
from chat   import Chat
from logger import Logger

class Streak:
    connection  = None
    logger      = Logger("Streak")

    @classmethod
    def setConnection(cls, connection) -> None:
        cls.connection = connection

    def __init__(self):
        self.chat = Chat()

    async def getMatches(self, beginIndex: int, endIndex: int) -> Optional[dict]:
        params = {"begIndex": beginIndex, "endIndex": endIndex}
        matchHistory    = await (await self.connection.request("get", f"/lol-match-history/v1/products/lol/current-summoner/matches", params=params)).json()
        matches         = matchHistory.get("games", {})

        if not matches:
            self.logger.log.debug("No matches found.")
            return

        return matches

    async def getPreviousMatch(self) -> Optional[dict]:
        matches = await self.getMatches(0, 0)
        games   = matches.get("games", [])

        if not games:
            self.logger.log.debug("No previous match found.")
            return
        
        return games[0]

    
    async def isMatchWin(self, match: dict) -> Optional[bool]:
        participants = match.get("participants", [])

        if not participants:
            self.logger.log.debug("participants error")
            return

        stats = participants[0].get("stats")

        if not stats:
            self.logger.log.debug("stats error")
            return

        win = stats.get("win")
        return win
    
    async def getStreak(self, win: bool) -> int:
        streak      = 1
        beginIndex  = 1 # 'gameIndexBegin'
        endIndex    = 5 # 'gameIndexEnd'
        indexCount  = 5 # 'gameCount'
        streakEnd   = False

        while True:
            matches = await self.getMatches(beginIndex, endIndex)
            
            if not matches:
                self.logger.log.debug(f"Failed to get matches data ({beginIndex}-{endIndex})")
                return
            
            games   = matches.get("games", [])

            if not games:
                self.logger.log.debug("Failed to get games data")
                return

            for game in games:
                curWin = await self.isMatchWin(game)

                if curWin is None:
                    self.logger.log.debug("Failed to get win")
                    return

                if curWin != win:
                    streakEnd = True
                    break
                streak += 1

            if streakEnd:
                break

            beginIndex  += indexCount
            endIndex    += indexCount
        return streak

    async def checkStreak(self):
        match = await self.getPreviousMatch()

        if not match:
            self.logger.log.info("No previous match")
            return
        
        isPreviousMatchWin = await self.isMatchWin(match)

        if isPreviousMatchWin is None:
            self.logger.log.info("No matches found")
            return
        
        streak = await self.getStreak(isPreviousMatchWin)

        if not streak:
            self.logger.log.info("Failed to count streak.")
            return

        streakType = "연승 중!"
        if isPreviousMatchWin is False:
            streakType = "연패 중.."
        
        if streak > 1:
            await self.chat.SendMessage(f"[Streak] {streak} {streakType}")