from actions import Action


class CheckQAOrNot(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please judge whether to ask questions for the user story."
        rsp = await self._aask(prompt)
        return rsp