from actions import Action

class SpeakUserStory(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "You are a end user,please write user stories."
        rsp = await self._aask(prompt)
        return rsp