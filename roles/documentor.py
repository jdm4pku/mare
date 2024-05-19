from typing import Any, Coroutine
from roles import Role
from actions import UpdateAnalysisReport
from actions import WriteSpecifications
from actions import ReviewSpecifications
from actions import UpdateSpecifications
from utils.common import any_to_str_set,any_to_str

class Documentor(Role):
    name:str = "Carol"
    profile: str = "Documentor"
    goal: str = ""
    constraints: str = ""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([WriteSpecifications,UpdateSpecifications])
        # Set events or actions the Architect should watch or be aware of
        self._watch([UpdateAnalysisReport,ReviewSpecifications])

    def _think(self):
        if not self.rc.news:
            return None
        msg = self.rc.news[0]
        if msg.cause_by in any_to_str_set(UpdateAnalysisReport):
            self.rc.todo = WriteSpecifications()
        elif msg.cause_by in any_to_str_set(ReviewSpecifications):
            self.rc.todo = UpdateAnalysisReport