from typing import Optional
from chat   import Chat
from logger import Logger
from options import Options

class Streak:
    connection  = None
    logger      = Logger("Streak")
    options     = Options()

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
        # to do: change const and get matches in once
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
        
        if streak > 1:
            if isPreviousMatchWin is True:
                self.logger.log.info(f"{streak} 연승 중!")
                await self.chat.SendMessage((await self.options.getOption("CoreFeature", "StreakWin")).format(streak=streak))
            elif isPreviousMatchWin is False:
                self.logger.log.info(f"{streak} 연패 중..")
                await self.chat.SendMessage((await self.options.getOption("CoreFeature", "StreakLose")).format(streak=streak))