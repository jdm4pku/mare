from actions import Action

class WriteReqList(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please write req list."
        rsp = await self._aask(prompt)
        return rsp