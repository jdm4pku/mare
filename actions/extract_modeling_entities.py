from actions import Action


class ExtractModelingEntity(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please extract modeling entities."
        rsp = await self._aask(prompt)
        return rsp
    