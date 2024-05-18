from actions import Action

class ReviewReqList(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please review the writen the req list."
        rsp = await self._aask(prompt)
        return rsp