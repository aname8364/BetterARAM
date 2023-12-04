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

    def dump(self) -> None:
        with open(self.optionPath, "w", encoding="UTF-8") as file:
            dump(self.optionData, file, ensure_ascii=False, indent=4)

    def load(self) -> None:
        with open(self.optionPath, "r", encoding="UTF-8") as file:
            self.optionData = load(file)

    def start(self) -> None:
        if not isfile(self.optionPath):
            self.dump()
        self.load()
    
    async def getOption(self, optionGroup: str, optionName: str, defaultValue: T = None) -> T:
        if not (group := self.optionData.get(optionGroup)):
            return defaultValue
        
        if not (option := group.get(optionName)):
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