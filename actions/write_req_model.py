from actions import Action

class WriteReqModel(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please write the requirements model in markdown table."
        rsp = await self._aask(prompt)
        return rsp