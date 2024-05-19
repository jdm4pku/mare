from typing import Any, Coroutine
from roles import Role
from actions import UpdateReqModel
from actions import CheckMiss
from actions import CheckAmbiguity
from actions import CheckConsistency
from actions import WriteAnalysisReport
from actions import ReviewAnalysisReport
from actions import UpdateAnalysisReport
from utils.common import any_to_str,any_to_str_set

class Analyst(Role):
    name:str = "Alex"
    profile: str = "Analyst"
    goal: str = ""
    constraints: str = ""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([CheckMiss,CheckAmbiguity,CheckConsistency,WriteAnalysisReport,UpdateAnalysisReport])
        # Set events or actions the Architect should watch or be aware of
        self._watch([UpdateReqModel,CheckMiss,CheckAmbiguity,CheckConsistency,ReviewAnalysisReport])

    def _think(self):
        if not self.rc.news:
            return None
        msg = self.rc.news[0]
        if msg.cause_by in any_to_str_set([UpdateReqModel]):
            self.rc.todo = CheckMiss()
        elif msg.cause_by in any_to_str_set([CheckMiss]):
            self.rc.todo = CheckAmbiguity()
        elif msg.cause_by in any_to_str_set([CheckConsistency]):
            self.rc.todo = WriteAnalysisReport()
        elif msg.cause_by in any_to_str_set([ReviewAnalysisReport]):
            self.rc.todo = UpdateAnalysisReport()
        return self.rc.todo


