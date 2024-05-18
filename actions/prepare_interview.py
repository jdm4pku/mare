from actions import Action

class PrepareIntervew(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    async def run(self,topic):
        prompt = "Requirement: Provide a list of questions for the interviewer to ask the interviewee, by reading the resume of the interviewee in the context. Attention: Provide as markdown block as the format above, at least 10 questions."
        rsp = await self._aask(prompt)
        return rsp