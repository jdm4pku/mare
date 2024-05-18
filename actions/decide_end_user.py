from actions import Action


class DecideEndUser(Action):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    async def run(self):
        prompt = "Please decides the end user for system."
        rsp = await self._aask(prompt)
        return rsp
