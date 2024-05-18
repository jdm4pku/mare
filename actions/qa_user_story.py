from actions import Action

class QAUserStory(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please ask question for the written user story."
        rsp = await self._aask(prompt)
        return rsp