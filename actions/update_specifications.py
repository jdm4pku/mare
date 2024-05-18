from actions import Action

class UpdateSpecifications(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please write the specifications."
        rsp = await self._aask(prompt)
        return rsp
    