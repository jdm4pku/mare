from roles import Role
from actions import UpdateReqList
from actions import ExtractModelingEntity
from actions import PredictRelations
from actions import WriteReqModel
from actions import ReviewReqModel
from actions import UpdateReqModel
from actions import CheckMiss
from schema import Message
from utils.common import any_to_str,any_to_name,any_to_str_set
import ast
import json
from itertools import combinations
from logs import logger

def get_entites_and_means(req_model):
    if req_model == "problem diagram":
        entitis = {
            "machine domain": "is the system or software that you want to design and build. ",
            "physical device": "is the physical device connected with the system or controller, which can be used to get/send/receive data/info.",
            "environment entities": "is the environment entities connected with the system or controller in the real world",
            "shared phenomenon": "is a set of shared events, states and values between the connected entities.",
            "Requirements":"is the aim of the system to be developed."
        }
        examples = {
            "machine domain": ["the smart home control system","the automated driving system"],
            "physical device": ["the sensor","the light","the thruster"],
            "environment entities":["the people","the car","the home","the sun"],
            "shared phenomenon":["the temperature value","turn on the light"],
            "Requirements":["to control the environment of the home","to driving the car automatically"]
        }
        return entitis,examples


def get_relations_and_means():
    rel = "a. Interface   b. Requirements reference    c.Requirements constraint   d. without relation\n"
    rel += "Here are the explanations for these relationships.\n"
    rel += "Interface: is an interface of shared phenomena between the connected entities. The interface relation exists between Machine Domain and Shared Phenomena, between Physical Device and Shared Phenomena, between Environment Entity and Shared Phenomena.\n"
    rel += "Requirements reference: is reference relation between Requirements Domain and other entities.\n"
    rel += "Requirements constraint: is constrain relation between Requirements Domain and other entities. It means the Requirements Domains does not just refer to the phenomena but constrains them. \n"
    examples = "" # todo
    return rel,examples
class Modeler(Role):
    name:str = "Greek"
    profile: str = "Modeler"
    goal: str = ""
    constraints: str = ""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([ExtractModelingEntity,PredictRelations,WriteReqModel,UpdateReqModel])
        # Set events or actions the Architect should watch or be aware of
        self._watch([UpdateReqList,ExtractModelingEntity,PredictRelations,ReviewReqModel,CheckMiss])
    
    async def _think(self):
        if not self.rc.news:
            return None
        msg = self.rc.news[0]
        if msg.cause_by in any_to_str_set([UpdateReqList]):
            self.rc.todo = ExtractModelingEntity()
        elif msg.cause_by in any_to_str_set([ExtractModelingEntity]):
            self.rc.todo = PredictRelations()
        elif msg.cause_by in any_to_str_set([PredictRelations]):
            self.rc.todo = WriteReqModel()
        elif msg.cause_by in any_to_str_set([ReviewReqModel]):
            self.rc.todo = UpdateReqModel()
        return self.rc.todo
    
    async def _act(self) -> Message:
        if self.rc.todo is None:
            return None
        if isinstance(self.rc.todo,ExtractModelingEntity):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            req_list = self.rc.memory.get_by_action(UpdateReqList)
            entities,examples = get_entites_and_means("problem diagram")
            model_result = {}
            for key,value in entities.items():
                exam = examples[key]
                model_entities = await self.rc.todo.run(key,value,exam,req_list)
                model_result[key] = ast.literal_eval(model_entities)
            
            msg = Message(
                content=json.dumps(model_result),
                role =self.profile,
                cause_by = ExtractModelingEntity,
                send_to = self,
                sent_from = self 
            )
            return msg
        elif isinstance(self.rc.todo,PredictRelations):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            req_list = self.rc.memory.get_by_action(UpdateReqList)
            extracted_entites = self.rc.memory.get_by_action(ExtractModelingEntity)
            entities_dict = json.loads(extracted_entites)
            entities_list = []
            rels,examples = get_relations_and_means("prodiagram examples")
            for type,entity_list in entities_dict:
                for entity in entity_list:
                    entities_list.append(f"{entity}({type})")
            unique_pairs = list(combinations(entities_list, 2))
            relations = {}
            for pair in unique_pairs:
                rel_type = await self.rc.todo.run(pair,rels,req_list)
                if "without relation" in rel_type:
                    pass
                else:
                    if rel_type in relations:
                        relations[rel_type].append(f"<{pair[0]},{pair[1]}>")
                    else:
                        relations[rel_type] = []

            msg = Message(
                content=json.dumps(relations),
                role =self.profile,
                cause_by = PredictRelations,
                send_to = self,
                sent_from = self 
            )
            return msg
        
        elif isinstance(self.rc.todo,WriteReqModel):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            req_list = self.rc.memory.get_by_action(UpdateReqList)
            entities = self.rc.memory.get_by_action(ExtractModelingEntity)
            relations =self.rc.memory.get_by_actions(PredictRelations)
            req_model = await self.rc.todo.run(entities,relations,req_list)
            msg = Message(
                content=req_model,
                role =self.profile,
                cause_by = WriteReqModel,
                send_to = self,
                sent_from = self 
            )
            return msg
        elif isinstance(self.rc.todo,UpdateReqModel):
            logger.info(f"{self.profile}: to do {self.rc.todo}")
            origin_model = self.rc.memory.get_by_action(WriteReqModel)
            update_advice = self.rc.memory.get_by_action(ReviewReqModel)
            new_model = await self.rc.todo.run(origin_model,update_advice)


            


            



        
        