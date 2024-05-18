from actions import Action


class UpdateReqList(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt= "Please update the ReqList."
        rsp = await self._aask(prompt)
        return rsp