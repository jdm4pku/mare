from action import Action

class ReviewAnalysisReport(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Please write the analysis report."
        rsp = await self._aask(prompt)
        return rsp