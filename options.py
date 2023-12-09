from os.path    import isfile
from json       import dump, load
from typing     import TypeVar

T = TypeVar("T")

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
    def dump(cls) -> None:
        with open(cls.optionPath, "w", encoding="UTF-8") as file:
            dump(cls.optionData, file, ensure_ascii=False, indent=4)

    @classmethod
    def load(cls) -> None:
        with open(cls.optionPath, "r", encoding="UTF-8") as file:
            cls.optionData = load(file)

    @classmethod
    def start(cls) -> None:
        if not isfile(cls.optionPath):
            cls.dump()
        cls.load()
    
    async def getOption(self, optionGroup: str, optionName: str, defaultValue: T = None) -> T:
        if (group := self.optionData.get(optionGroup)) is None:
            return defaultValue
    
        if (option := group.get(optionName)) is None:
            return defaultValue
        
        return option
        
async def main() -> None:
    options = Options()
    options.start()

    lang = await options.getOption("DataDragonAPI", "Language")
    print(lang)
    
if __name__ == "__main__":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())