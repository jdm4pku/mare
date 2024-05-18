from actions import Action

class CheckMiss(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please check the missing the requirements."
        rsp = await self._aask(prompt)
        return rsp