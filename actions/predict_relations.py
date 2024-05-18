from actions import Action

class PredictRelations(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please predict the relations between the entities."
        rsp = await self._aask(prompt)
        return rsp