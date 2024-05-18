from actions import Action

class AnswerQA(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please answer qa."
        rsp = await self._aask(prompt)
        return rsp
    