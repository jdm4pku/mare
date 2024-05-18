from action import Action

class CheckConsistency(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please get some domain knowlege for the developing system."
        rsp = await self._aask(prompt)
        return rsp