from roles import Role
from actions import WriteReqList
from actions import ReviewReqList
from actions import WriteReqModel
from actions import ReviewReqModel
from actions import WriteAnalysisReport
from actions import ReviewAnalysisReport
from actions import ReviewSpecifications
from actions import WriteSpecifications
from schema import Message
from utils.common import any_to_str_set,any_to_str
from logs import logger

class Human(Role):
    name:str = "human"
    profile: str = "Human"
    goal: str = ""
    constraints: str = ""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([ReviewReqList,ReviewReqModel,ReviewAnalysisReport,ReviewSpecifications])
        # Set events or actions the Architect should watch or be aware of
        self._watch([WriteReqList,WriteReqModel,WriteAnalysisReport,WriteSpecifications])
    
    async def _think(self):
        if not self.rc.news:
            return None
        msg = self.rc.news[0]
        if msg.cause_by in any_to_str_set([WriteReqList]):
            self.rc.todo = ReviewReqList()
        elif msg.cause_by in any_to_str_set([WriteReqModel]):
            self.rc.todo = ReviewReqModel()
        elif msg.cause_by in any_to_str_set([WriteAnalysisReport]):
            self.rc.todo = ReviewAnalysisReport()
        elif msg.cause_by in any_to_str_set([WriteSpecifications]):
            self.rc.todo = ReviewSpecifications()
        return self.rc.todo
    
    async def _act(self) -> Message:
        if self.rc.todo is None:
            return None
        if isinstance(self.rc.todo,ReviewReqList):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            req_list = self.rc.memory.get_by_action(WriteReqList)
            req_list_advice = await self.rc.todo.run(req_list)
            msg = Message(
                content=req_list_advice,
                role=self.profile,
                cause_by = ReviewReqList,
                send_to ="Frank",
                sent_from = self)
            return msg
        elif isinstance(self.rc.todo,ReviewReqModel):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            req_model = self.rc.memory.get_by_action(WriteReqModel)
            req_model_advice = await self.rc.todo.run(req_model)
            msg = Message(
                content = req_model_advice,
                role =self.profile,
                cause_by = ReviewReqModel,
                send_to = "Greek",
                sent_from = self
            )
            return msg
        
        
    

        