from os.path    import isfile
from json       import dump, load

class Options:
    optionPath = "options.json"
    optionData = {
        "CoreFeature": {
            "UseEnterMessage"   : True,
            "EnterMessage"      : "BetterARAM을 사용중이에요!",

            "UseCommand"        : True,
            "CommandMessage"    : "명령어가 {count}개 있어요: /me 또는 /team",

            "UseAutoSwap"       : True,
            "AutoSwapMessage"   : "{champion}를 벤치에서 가져왔어요. (우선순위: {priority})", 

            "UseStreak"         : True,
            "StreakWin"         : "{streak} 연승 중!",
            "StreakLose"        : "{streak} 연패 중..",

            "UseAutoAccept"     : True
        },
        "SubFeature": {
            "SendMessage"   : True
        },
        "DataDragonAPI": {
            "Language"      : "ko_KR"
        }
    }

    @classmethod
    def checkOptionsPath(cls):
        if not isfile(cls.optionPath):
            with open(cls.optionPath, "w", encoding="UTF-8") as file:
                dump(cls.optionData, file, ensure_ascii=False, indent=4)

    @classmethod
    def loadOptions(cls):
        cls.checkOptionsPath()
        with open(cls.optionPath, "r", encoding="UTF-8") as file:
            cls.optionData = load(file)
    
    async def getOption(self, optionGroup: str, optionName: str, defaultValue = None):
        if not (group := self.optionData.get(optionGroup)):
            return defaultValue
        
        if not (option := group.get(optionName)):
            return defaultValue
        
        return option
        