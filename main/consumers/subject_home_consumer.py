'''
websocket session list
'''
from pickle import TRUE
from asgiref.sync import sync_to_async

import logging
import copy
import json
import string
from copy import copy
from copy import deepcopy

from django.core.exceptions import  ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from main.consumers import SocketConsumerMixin
from main.consumers import StaffSubjectUpdateMixin

from main.forms import EndGameForm

from main.models import Session
from main.models import SessionPlayer
from main.models import SessionPlayerChat
from main.models import SessionPlayerPart
from main.models import SessionPlayerPartPeriod
from main.models import ParameterSetRandomOutcome

from main.globals import ChatTypes
from main.globals import round_half_away_from_zero
from main.globals import ExperimentPhase

from main.decorators import check_sesison_started_ws

import main

class SubjectHomeConsumer(SocketConsumerMixin, StaffSubjectUpdateMixin):
    '''
    websocket session list
    '''    

    session_player_id = 0   #session player id number
    
    async def get_session(self, event):
        '''
        return a list of sessions
        '''
        logger = logging.getLogger(__name__) 
        logger.info(f"Get Session {event}")

        self.connection_uuid = event["message_text"]["playerKey"]
        self.connection_type = "subject"
        self.session_id = await sync_to_async(take_get_session_id)(self.connection_uuid)

        await self.update_local_info(event)

        result = await sync_to_async(take_get_session_subject)(self.session_player_id)

        #build response
        message_data = {"status":{}}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message,}, cls=DjangoJSONEncoder))
   
    async def chat(self, event):
        '''
        take chat from client
        '''        
        result = await sync_to_async(take_chat)(self.session_id, self.session_player_id, event["message_text"])

        if result["value"] == "fail":
            await self.send(text_data=json.dumps({'message': result}, cls=DjangoJSONEncoder))
            return

        event_result = result["result"]

        subject_result = {}
        subject_result["chat_type"] = event_result["chat_type"]
        subject_result["sesson_player_target"] = event_result.get("sesson_player_target", -1)
        subject_result["chat"] = event_result["chat_for_subject"]
        subject_result["value"] = result["value"]

        staff_result = {}
        staff_result["chat"] = event_result["chat_for_staff"]

        message_data = {}
        message_data["status"] = subject_result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send reply to sending channel
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        #if success send to all connected clients
        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_chat",
                 "subject_result": subject_result,
                 "staff_result": staff_result,
                 "sender_channel_name": self.channel_name},
            )

    async def name(self, event):
        '''
        take name and id number
        '''
        result = await sync_to_async(take_name)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_name",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )
    
    async def choice(self, event):
        '''
        take choice
        '''
        result = await sync_to_async(take_choice)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result
        message_data["status"]["result"]["player_id"] = self.session_player_id

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_choice",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )

    async def next_instruction(self, event):
        '''
        advance instruction page
        '''
        result = await sync_to_async(take_next_instruction)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_next_instruction",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )
    
    async def finish_instructions(self, event):
        '''
        finish instructions
        '''
        result = await sync_to_async(take_finish_instructions)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_finish_instructions",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )
    
    async def ready_to_go_on(self, event):
        '''
        subject is finsihed reviewing results of part
        '''
        result = await sync_to_async(take_ready_to_go_on)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_ready_to_go_on",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )

    #consumer updates
    async def update_start_experiment(self, event):
        '''
        start experiment on subjects
        '''
        #logger = logging.getLogger(__name__) 
        #logger.info(f'update start subjects {self.channel_name}')

        await self.update_local_info(event)

        #get session json object
        result = await sync_to_async(take_get_session_subject)(self.session_player_id)
        result["instruction_pages"] = await sync_to_async(take_get_instruction_set)(self.session_player_id)
 
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        #if self.channel_name != event['sender_channel_name']:
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_reset_experiment(self, event):
        '''
        reset experiment on subjects
        '''
        #logger = logging.getLogger(__name__) 
        #logger.info(f'update start subjects {self.channel_name}')

        #get session json object
        result = await sync_to_async(take_get_session_subject)(self.session_player_id)

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''

        message_data = {}
        message_data["status"] =  event["subject_result"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        if self.channel_name == event['sender_channel_name']:
            return
        
        if message_data['status']['chat_type'] == "Individual" and \
           message_data['status']['sesson_player_target'] != self.session_player_id and \
           message_data['status']['chat']['sender_id'] != self.session_player_id:

           return

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_local_info(self, event):
        '''
        update connection's information
        '''
        result = await sync_to_async(take_update_local_info)(self.session_id, self.connection_uuid, event)

        logger = logging.getLogger(__name__) 
        logger.info(f"update_local_info {result}")

        self.session_player_id = result["session_player_id"]

    async def update_time(self, event):
        '''
        update running, phase and time status
        '''

        event_data = deepcopy(event["data"])

        #remove other player earnings
        for session_players_earnings in event_data["result"]["session_player_earnings"]:
            if session_players_earnings["id"] == self.session_player_id:
                event_data["result"]["session_player_earnings"] = session_players_earnings
                break
        
        #remove none group memebers
        session_players = []
        for session_player in event_data["result"]["session_players"]:
            session_players.append(session_player)
        
        #remove other player notices
        notice_list = []
        for session_player_notice in event_data.get("notice_list", []):
            if session_player_notice["session_player_id"] == self.session_player_id:
                notice_list.append(session_player_notice)
                break

        event_data["notice_list"] = notice_list   

        event_data["result"]["session_players"] = session_players

        message_data = {}
        message_data["status"] = event_data

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_connection_status(self, event):
        '''
        handle connection status update from group member
        '''
        pass

    async def update_name(self, event):
        '''
        no group broadcast of name to subjects
        '''
        pass
    
    async def update_choice(self, event):
        '''
        no group broadcast of choice to subjects
        '''
        pass
    
    async def update_next_period(self, event):
        '''
        update session period
        '''

        message_data = {}
        message_data["status"] = event["data"]
        message_data["status"]["result"]["current_choice"] = await sync_to_async(take_get_subject_current_choice)(self.session_player_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_next_phase(self, event):
        '''
        update session phase
        '''

        # result = await sync_to_async(take_update_next_phase)(self.session_id, self.session_player_id)

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_next_instruction(self, event):
        '''
        no group broadcast of avatar to current instruction
        '''
        pass
    
    async def update_finish_instructions(self, event):
        '''
        no group broadcast of avatar to current instruction
        '''
        pass
    
    async def update_ready_to_go_on(self, event):
        '''
        no group broadcast ready to go on
        '''
        pass

    async def update_survey_complete(self, event):
        '''
        no group broadcast of survey complete
        '''
        pass

    async def update_final_results(self, event):
        '''
        send final results
        '''

        message_data = {}
        message_data["status"] = {"value":"success", 
                                  "result": await sync_to_async(take_get_update_final_result)(self.session_id, self.session_player_id)}

        message = {}
        message["messageType"] = "final_results"
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_current_session_part_result(self, event):
        '''
        send current part results
        '''

        message_data = {}
        message_data["status"] = {"value":"success", 
                                  "result": await sync_to_async(take_get_update_current_session_part_result)(self.session_id, self.session_player_id)}

        message = {}
        message["messageType"] = "update_current_session_part_result"
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_refresh_screens(self, event):
        '''
        refresh staff screen
        '''
        message_data = {}
        message_data["status"] = {"value":"success", 
                                  "result": await sync_to_async(take_get_session_subject)(self.session_player_id)}

        message = {}
        message["messageType"] = "refresh_screens"
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        pass

#local sync functions  
def take_get_session_subject(session_player_id):
    '''
    get session info for subject
    '''
    #session_id = data["sessionID"]
    #uuid = data["uuid"]

    #session = Session.objects.get(id=session_id)
    try:
        session_player = SessionPlayer.objects.get(id=session_player_id)
        
        return {"session" : session_player.session.json_for_subject(session_player), 
                "session_player" : session_player.json(),
                "current_choice" : session_player.json_current_choice() }

    except ObjectDoesNotExist:
        return {"session" : None, 
                "session_player" : None,
                "current_choice" : None}

def take_get_update_current_session_part_result(session_id, session_player_id):
    '''
    return result for current session_part
    '''
    try:
        session_player = SessionPlayer.objects.get(id=session_player_id)
        
        return {"session" : session_player.session.json_for_subject(session_player), 
                "session_player" : session_player.json(),
                "current_choice" : session_player.json_current_choice(),}
                 

    except ObjectDoesNotExist:
        return {"session" : None, 
                "session_player" : None,
                "current_choice" : None
                }

def take_get_update_final_result(session_id, session_player_id):
    '''
    return result for current session_part
    '''
    logger = logging.getLogger(__name__) 

    try:
        logger.info(f"take_get_update_final_result: Start {session_player_id}")

        session_player = SessionPlayer.objects.get(id=session_player_id)
        session = Session.objects.get(id=session_id)

        return {
                "session_player" : session_player.json(),
                "earnings" : f'{session_player.earnings:.2f}',
                "current_experiment_phase" : session.current_experiment_phase,
                 }

    except ObjectDoesNotExist:
        return {
                "earnings" : None,
                "session_player" : None,
                "current_experiment_phase" : None,
                }

def take_get_instruction_set(session_player_id):
    '''
    return the instruction set
    '''
    try:
        session_player = SessionPlayer.objects.get(id=session_player_id)

        return session_player.get_instruction_set()

    except ObjectDoesNotExist:
        return []

def take_get_subject_current_choice(session_player_id):
    '''
    return the current choice for session_player_id
    '''
    try:
        session_player = SessionPlayer.objects.get(id=session_player_id)
        
        return session_player.json_current_choice()

    except ObjectDoesNotExist:
        return None

def take_get_session_id(player_key):
    '''
    get the session id for the player_key
    '''
    session_player = SessionPlayer.objects.get(player_key=player_key)

    return session_player.session.id
  
def take_chat(session_id, session_player_id, data):
    '''
    take chat from client
    sesson_id : int : id of session
    session_player_id : int : id of session player
    data : json : incoming json data
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"take chat: {session_id} {session_player_id} {data}")

    try:
        recipients = data["recipients"] 
        chat_text = data["text"]
    except KeyError:
         return {"value" : "fail", "result" : {"message" : "Invalid chat."}}

    result = {}
    #result["recipients"] = []

    session = Session.objects.get(id=session_id)
    session_player = session.session_players_a.get(id=session_player_id)
    
    session_player_chat = SessionPlayerChat()

    session_player_chat.session_player = session_player
    session_player_chat.session_part = session.current_session_part

    if not session.started:
        return  {"value" : "fail", "result" : {"message" : "Session not started."}, }
        
    if session.finished:
        return {"value" : "fail", "result" : {"message" : "Session finished."}}

    if session.current_experiment_phase != main.globals.ExperimentPhase.RUN:
        return {"value" : "fail", "result" : {"message" : "Session not running."}}

    if recipients == "all":
        session_player_chat.chat_type = ChatTypes.ALL
    else:
        if not session.parameter_set.private_chat:
            logger.warning(f"take chat: private chat not enabled :{session_id} {session_player_id} {data}")
            return {"value" : "fail",
                    "result" : {"message" : "Private chat not allowed."}}

        session_player_chat.chat_type = ChatTypes.INDIVIDUAL

    result["chat_type"] = session_player_chat.chat_type
    result["recipients"] = []

    session_player_chat.text = chat_text
    session_player_chat.time_remaining = session.time_remaining

    session_player_chat.save()

    if recipients == "all":
        session_player_chat.session_player_recipients.add(*session.session_players_a.all())

        result["recipients"] = [i.id for i in session.session_players_a.all()]
    else:
        sesson_player_target = SessionPlayer.objects.get(id=recipients)

        if sesson_player_target in session.session_players_a.all():
            session_player_chat.session_player_recipients.add(sesson_player_target)
        else:
            session_player_chat.delete()
            logger.warning(f"take chat: chat at none group member : {session_id} {session_player_id} {data}")
            return {"value" : "fail", "result" : {"Player not in group."}}

        result["sesson_player_target"] = sesson_player_target.id

        result["recipients"].append(session_player.id)
        result["recipients"].append(sesson_player_target.id)
    
    result["chat_for_subject"] = session_player_chat.json_for_subject()
    result["chat_for_staff"] = session_player_chat.json_for_staff()

    session_player_chat.save()

    return {"value" : "success", "result" : result}

def take_update_local_info(session_id, player_key, data):
    '''
    update connection's information
    '''

    try:
        session_player = SessionPlayer.objects.get(player_key=player_key)
        session_player.save()

        return {"session_player_id" : session_player.id}
    except ObjectDoesNotExist:      
        return {"session_player_id" : None}

def take_name(session_id, session_player_id, data):
    '''
    take name and student id at end of game
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take name: {session_id} {session_player_id} {data}")

    form_data_dict =  data["formData"]

    # try:
    #     form_data = data["formData"]

    #     # for field in form_data:            
    #     #     form_data_dict[field["name"]] = field["value"]

    # except KeyError:
    #     logger.warning(f"take_name , setup form: {session_player_id}")
    #     return {"value" : "fail", "errors" : {f"name":["Invalid Entry."]}}
    
    session = Session.objects.get(id=session_id)
    session_player = session.session_players_a.get(id=session_player_id)

    if not session.current_experiment_phase == ExperimentPhase.NAMES:
        return {"value" : "fail", "errors" : {f"name":["Session not complete."]},
                "message" : "Session not complete."}

    logger.info(f'form_data_dict : {form_data_dict}')       

    form = EndGameForm(form_data_dict)
        
    if form.is_valid():
        #print("valid form") 

        session_player.name = form.cleaned_data["name"]
        session_player.student_id = form.cleaned_data["student_id"]
        session_player.name_submitted = True

        session_player.name = string.capwords(session_player.name)

        session_player.save()    
        
        return {"value" : "success",
                "result" : {"id" : session_player_id,
                            "name" : session_player.name, 
                            "name_submitted" : session_player.name_submitted,
                            "student_id" : session_player.student_id}}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items()), "message" : ""}

def take_choice(session_id, session_player_id, data):
    '''
    take period choice
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take choice: {session_id} {session_player_id} {data}")

    data = data["data"]

    message = ""
    result = {"current_index" : data["current_index"]}

    try:
        session = Session.objects.get(id=session_id)
        session_player = session.session_players_a.get(id=session_player_id)

        # with transaction.atomic():
        session_player_part_period = SessionPlayerPartPeriod.objects.get(id=data["part_period_id"])
        session_player_part_period.choice = ParameterSetRandomOutcome.objects.get(id=data["random_outcome_id"])
        session_player_part_period.choice_length = data["time_span"]
        session_player_part_period.json_for_group(True)
        session_player_part_period.save()

        #"session_player.session_player_parts.0.session_player_part_periods.0.choice"
        indexes = session_player_part_period.get_part_period_indexes()
        part_number = indexes["part_number"]
        period_number = indexes["period_number"]
        session_player.session_player_parts_json[part_number]["session_player_part_periods"][period_number]["choice"] = session_player_part_period.choice.json()
        session_player.session_player_parts_json[part_number]["session_player_part_periods"][period_number]["choice_length"] = data["time_span"]
        session_player.save()

        result["session_player_parts"] = session_player.session_player_parts_json

    except ObjectDoesNotExist:      
        message = "Session Period Part not found"
        logger.error(f"take_choice : {message}")
        return {"value" : "fail", "errors" : {"text" : message}, "message" : message}
   
    return {"value" : "success", "errors" : {}, "message" : "", "result" : result}

def take_update_next_phase(session_id, session_player_id):
    '''
    return information about next phase of experiment
    '''

    logger = logging.getLogger(__name__) 

    try:
        session = Session.objects.get(id=session_id)
        session_player = SessionPlayer.objects.get(id=session_player_id)


        return {"value" : "success",
                "session" : session_player.session.json_for_subject(session_player),
                "session_player" : session_player.json()}

    except ObjectDoesNotExist:
        logger.warning(f"take_update_next_phase: session not found, session {session_id}, session_player_id {session_player_id}")
        return {"value" : "fail", "result" : {}, "message" : "Update next phase error"}

def take_next_instruction(session_id, session_player_id, data):
    '''
    take show next instruction page
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take next instruction: {session_id} {session_player_id} {data}")

    try:       

        session = Session.objects.get(id=session_id)
        session_part = session.current_session_part
        session_player = session.session_players_a.get(id=session_player_id)
        session_player_part = session_player.get_current_session_player_part()

        direction = data["direction"]

        #move to next instruction
        if direction == 1:
            #advance furthest instruction complete
            if session_player_part.current_instruction_complete < session_player_part.current_instruction:
                session_player_part.current_instruction_complete = copy(session_player_part.current_instruction)

            if session_player_part.current_instruction < session_part.parameter_set_part.instruction_set.instructions.count()-1:
                session_player_part.current_instruction += 1
            
            #check if last page, no actions on last page.
            if session_player_part.current_instruction == session_part.parameter_set_part.instruction_set.instructions.count()-1:
                session_player_part.current_instruction_complete = copy(session_player_part.current_instruction)
            
        elif session_player_part.current_instruction > 0:
             session_player_part.current_instruction -= 1

        session_player_part.save()

        #"session_player.session_player_parts.0.session_player_part_periods.0.choice"        
        part_number = session_player_part.session_part.parameter_set_part.part_number-1
        session_player.session_player_parts_json[part_number]["current_instruction"] = session_player_part.current_instruction
        session_player.session_player_parts_json[part_number]["current_instruction_complete"] = session_player_part.current_instruction_complete
        session_player.save()

    except ObjectDoesNotExist:
        logger.warning(f"take_next_instruction not found: {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Instruction Error."} 
    except KeyError:
        logger.warning(f"take_next_instruction key error: {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Instruction Error."}       
    
    return {"value" : "success",
            "result" : {"current_instruction" : session_player_part.current_instruction,
                        "id" : session_player_id,
                        "current_instruction_complete" : session_player_part.current_instruction_complete, 
                        }}

def take_finish_instructions(session_id, session_player_id, data):
    '''
    take finish instructions
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take finish instructions: {session_id} {session_player_id} {data}")

    try:       

        session = Session.objects.get(id=session_id)
        session_part = session.current_session_part
        session_player = session.session_players_a.get(id=session_player_id)
        session_player_part = session_player.get_current_session_player_part()

        session_player_part.instructions_finished = True
        session_player_part.save()

        part_number = session_player_part.session_part.parameter_set_part.part_number-1
        session_player.session_player_parts_json[part_number]["instructions_finished"] = session_player_part.instructions_finished
        session_player.save()

    except ObjectDoesNotExist:
        logger.warning(f"take_next_instruction : {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Error"}       
    
    return {"value" : "success",
            "result" : {"instructions_finished" : session_player_part.instructions_finished,
                        "id" : session_player_id,
                        "current_instruction_complete" : session_player_part.current_instruction_complete, 
                        }}

def take_ready_to_go_on(session_id, session_player_id, data):
    '''
    take ready to go on
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take ready to go on: {session_id} {session_player_id} {data}")

    data = data["data"]

    message = ""
    result = {"current_index" : data["current_index"]}

    try:       
        
        with transaction.atomic():
            session = Session.objects.get(id=session_id)
            session_player = session.session_players_a.get(id=session_player_id)
            session_player_part = SessionPlayerPart.objects.get(id=data["player_part_id"])
           
            session_player_part.results_complete = True
            session_player_part.save()

            part_number = session_player_part.session_part.parameter_set_part.part_number-1
            session_player.session_player_parts_json[part_number]["results_complete"] = session_player_part.results_complete
            session_player.save()

        result["session_player_part"] = session_player.session_player_parts_json[part_number]
        result["player_id"] = session_player_id

    except ObjectDoesNotExist:
        logger.warning(f"take_ready_to_go_on : {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Error"}       
    
    return {"value" : "success", "errors" : {}, "message" : "", "result" : result}