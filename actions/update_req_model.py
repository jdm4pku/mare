from actions import Action


class UpdateReqModel(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt= "Please update the Req Model."
        rsp = await self._aask(prompt)
        return rsp