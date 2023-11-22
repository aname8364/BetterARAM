from os.path    import isfile
from json       import dump, load

class Options:
    optionPath = "options.json"
    optionData = {
        "CoreFeature": {
            "UseCommand"    : True,
            "UseAutoSwap"   : True,
            "UseStreak"     : True
        },
        "SubFeature": {
            "SendMessage"   : True
        },
        "Other": {
            "EnterMessage"  : "BetterARAM을 사용중이에요!"
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
    
    async def getOption(self, optionGroup: str, optionName: str):
        if not (group := self.optionData.get(optionGroup)):
            return
        
        if not (option := group.get(optionName)):
            return
        
        return option
        