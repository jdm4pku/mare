from actions import Action

class CheckAmbiguity(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please check requirements ambiguity."
        rsp = await self._aask(prompt)
        return rsp
    