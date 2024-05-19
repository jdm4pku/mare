from roles import Role
from actions import UserRequirement,SearchDomainKnowledge,DecideEndUser
from actions import PrepareIntervew
from actions import SpeakUserStory
from actions import QAUserStory
from actions import AnswerQA
from actions import WriteReqList
from actions import ReviewReqList
from actions import UpdateReqList
from actions import CheckMiss
from actions import CheckAmbiguity
from actions import CheckConsistency
from utils.common import any_to_str_set
from schema import Message
from logs import logger
from roles.enduser import EndUser


QA_COUNT = 2
class Interviewer(Role):
    name:str = "Frank"
    profile: str = "Interviewer"
    goal: str = ""
    constraints: str = ""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.qa_count = 0
        # Initialize actions specific to the Architect role
        self.set_actions([SearchDomainKnowledge,DecideEndUser,PrepareIntervew,QAUserStory,WriteReqList,UpdateReqList])
        # Set events or actions the Architect should watch or be aware of
        self._watch([UserRequirement,SearchDomainKnowledge,DecideEndUser,SpeakUserStory,AnswerQA,ReviewReqList,CheckMiss,CheckAmbiguity,CheckConsistency])
    
    async def _think(self):
        if not self.rc.news:
            return None
        msg = self.rc.news[0]
        if msg.cause_by in any_to_str_set([UserRequirement]):
            self.rc.todo = SearchDomainKnowledge()
        elif msg.cause_by in any_to_str_set([SearchDomainKnowledge]):
            self.rc.todo = DecideEndUser()
        elif msg.cause_by in any_to_str_set([DecideEndUser]):
            self.rc.todo = PrepareIntervew()
        elif msg.cause_by in any_to_str_set([SpeakUserStory]):
            self.rc.todo = QAUserStory()
        elif msg.cause_by in any_to_str_set([AnswerQA]) and self.qa_count<QA_COUNT:
            self.rc.todo = QAUserStory()
        elif msg.cause_by in any_to_str_set([AnswerQA]) and self.qa_count==QA_COUNT:
            self.rc.todo = WriteReqList
        elif msg.cause_by in any_to_str_set([ReviewReqList]):
            self.rc.todo = UpdateReqList
        return self.rc.todo
    async def _act(self):
        if self.rc.todo is None:
            return None
        if isinstance(self.rc.todo,SearchDomainKnowledge):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            human_idea = self.get_memories(k=1)[0]
            domainknow = await self.rc.todo.run(human_idea)
            msg = Message(
                content=domainknow,
                role=self.profile,
                cause_by = SearchDomainKnowledge,
                send_to =self,
                sent_from = self)
            return msg
        elif isinstance(self.rc.todo,DecideEndUser):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            human_idea = self.rc.memory.get_by_action(UserRequirement)
            domainknow = self.rc.memory.get_by_action(SearchDomainKnowledge)
            enduser = await self.rc.todo.run(human_idea,domainknow)
            msg = Message(
                content=enduser,
                role = self.profile,
                cause_by = DecideEndUser,
                send_to = self,
                sent_from = self
            )
            return msg
        elif isinstance(self.rc.todo,PrepareIntervew):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            human_idea = self.rc.memory.get_by_action(UserRequirement)
            domainknow = self.rc.memory.get_by_action(SearchDomainKnowledge)
            enduser = self.rc.memory.get_by_action(DecideEndUser)
            interviewscript = await self.rc.todo.run(human_idea,domainknow,enduser)
            msg = Message(
                content = interviewscript,
                role = self.profile,
                cause_by = PrepareIntervew,
                # send_to = EndUser, # end user 的名字,
                sent_from = self
            )
            return msg
        elif isinstance(self.rc.todo,QAUserStory):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            self.qa_count +=1
            stories = self.rc.memory.get_by_action(SpeakUserStory)
            question = await self.rc.todo.run(stories)
            msg = Message(
                content = question,
                role = self.profile,
                cause_by = QAUserStory,
                send_to = "David", # end user 的名字,
                sent_from = self
            )
            return msg
        elif isinstance(self.rc.todo,WriteReqList):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            all_memories = self.get_memories()
            reqlist = await self.rc.todo.run(all_memories)
            msg = Message(
                content = reqlist,
                role = self.profile,
                cause_by = WriteReqList,
                send_to = "human",
                sent_from = self
            )
            return msg
        elif isinstance(self.rc.todo,UpdateReqList):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            req_list = self.rc.memory.get_by_action(WriteReqList)
            req_list_advice = self.rc.memory.get_by_action(ReviewReqList)
            update_req_list = self.rc.todo.run(req_list,req_list_advice)
            msg = Message(
                content = update_req_list,
                role =self.role,
                cause_by = UpdateReqList,
                send_to = "Greek",
                sent_from = self
            )
            return msg



        


            



        
    

        
        


    