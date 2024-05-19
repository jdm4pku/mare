from roles import Role
from actions import PrepareIntervew
from actions import SpeakUserStory
from actions import QAUserStory
from actions import AnswerQA
from actions import DecideEndUser
from schema import Message
import ast
from utils.common import any_to_str,any_to_str_set
from logs import logger

class EndUser(Role):
    name:str = "David"
    profile: str = "EndUser"
    goal: str = ""
    constraints: str = ""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([SpeakUserStory,AnswerQA])
        # Set events or actions the Architect should watch or be aware of
        self._watch([PrepareIntervew,QAUserStory])
    
    async def _think(self):
        if not self.rc.news:
            return None
        msg = self.rc.news[0]
        if msg.cause_by in any_to_str_set([PrepareIntervew]):
            self.rc.todo = SpeakUserStory()
        elif msg.cause_by in any_to_str_set([QAUserStory]):
            self.rc.todo = AnswerQA()
        return self.rc.todo
    
    async def _act(self) -> Message:
        if self.rc.todo is None:
            return None
        if isinstance(self.rc.todo,SpeakUserStory):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            enduser = self.rc.memory.get_by_action(DecideEndUser)
            enduserlist = ast.literal_eval(enduser)
            user_stories_list = []
            for enduser in enduserlist:
                usertories = await self.rc.todo.run()
                user_stories_list.append(usertories)
            total_user_stories = '\n'.join(user_stories_list)
            msg = Message(
                content = total_user_stories,
                role = self.profile,
                cause_by = SpeakUserStory,
                send_to = "Frank",
                send_from = self
            )
            return msg
        elif isinstance(self.rc.todo,AnswerQA):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            enduser = self.rc.memory.get_by_action(DecideEndUser)
            enduserlist = ast.literal_eval(enduser)
            user_stories_list = []
            for enduser in enduserlist:
                usertories = await self.rc.todo.run()
                user_stories_list.append(usertories)
            total_user_stories = '\n'.join(user_stories_list)
            msg = Message(
                content = total_user_stories,
                role = self.profile,
                cause_by = SpeakUserStory,
                send_to = "Frank",
                send_from = self
            )
            return msg
        

        
        
