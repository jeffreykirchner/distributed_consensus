'''
websocket session list
'''
from decimal import Decimal, DecimalException

from asgiref.sync import sync_to_async

import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder

from main.consumers import SocketConsumerMixin
from main.consumers import StaffSubjectUpdateMixin

from main.forms import SessionForm
from main.forms import ParameterSetForm
from main.forms import ParameterSetPlayerForm
from main.forms import ParameterSetPlayerPartForm
from main.forms import ParameterSetPartForm
from main.forms import ParameterSetPartPeriodForm
from main.forms import ParameterSetRandomOutcomeForm
from main.forms import ParameterSetLabelsForm
from main.forms import ParameterSetLabelsPeriodForm

from main.models import Session
from main.models import ParameterSetPlayer
from main.models import ParameterSetPlayerPart
from main.models import ParameterSetPart
from main.models import ParameterSetPartPeriod
from main.models import ParameterSetRandomOutcome
from main.models import ParameterSetLabels
from main.models import ParameterSetLabelsPeriod

import main

class StaffSessionParametersConsumer(SocketConsumerMixin, StaffSubjectUpdateMixin):
    '''
    websocket session list
    '''    

    async def get_session(self, event):
        '''
        return a list of sessions
        '''
        logger = logging.getLogger(__name__) 
        logger.info(f"Get Session {event}")

        #build response
        message_data = {}
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message,}, cls=DjangoJSONEncoder))
    
    async def update_parameterset(self, event):
        '''
        update a parameterset
        '''
        #build response
        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_parameterset"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))


    async def update_parameterset_player(self, event):
        '''
        update a parameterset player
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_player)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_parameterset_player"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder)) 
    
    async def update_parameterset_player_part(self, event):
        '''
        update a parameterset player part
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_player_part)(event["message_text"])
        #message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_parameterset_player_part"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder)) 

    async def remove_parameterset_player(self, event):
        '''
        remove a parameterset player
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_remove_parameterset_player)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "remove_parameterset_player"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))   
    
    async def add_parameterset_player(self, event):
        '''
        add a parameterset player
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_add_parameterset_player)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "add_parameterset_player"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    
    async def update_parameterset_random_outcome(self, event):
        '''
        update a parameterset random outcome
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_random_outcome)(event["message_text"])
        message_data["session"] = {}

        message = {}
        message["messageType"] = "update_parameterset_random_outcome"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder)) 

    async def remove_parameterset_random_outcome(self, event):
        '''
        remove a parameterset random outcome
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_remove_parameterset_random_outcome)(event["message_text"])
        message_data["session"] = {}

        message = {}
        message["messageType"] = "remove_parameterset_random_outcome"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))   
    
    async def add_parameterset_random_outcome(self, event):
        '''
        add a parameterset random outcome
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_add_paramterset_random_outcome)(event["message_text"])
        message_data["session"] = {}

        message = {}
        message["messageType"] = "add_parameterset_random_outcome"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    

    async def update_parameterset_part(self, event):
        '''
        update a parameterset part
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_part)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_parameterset_part"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder)) 
    
    async def update_parameterset_part_period(self, event):
        '''
        update a parameterset part period
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_part_period)(event["message_text"])
        #message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_parameterset_part_period"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder)) 
    
    async def update_parameterset_randomize_part_periods(self, event):
        '''
        update a parameterset part period
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_randomize_part_periods)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "get_session"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder)) 


    async def update_parameterset_labels(self, event):
        '''
        update a parameterset labels
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_labels)(event["message_text"])
        message_data["session"] = {}

        message = {}
        message["messageType"] = "update_parameterset_labels"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_parameterset_labels_period(self, event):
        '''
        update a parameterset labels
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_labels_period)(event["message_text"])
        #message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_parameterset_labels_period"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_parameterset_randomize_labels(self, event):
        '''
        update a parameterset labels
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_randomize_labels)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "get_session"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def import_parameters(self, event):
        '''
        import parameters from another session
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_import_parameters)(event["message_text"])

        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "import_parameters"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_parameters(self, event):
        '''
        download parameters to a file
        '''
        #download parameters to a file
        message = {}
        message["messageType"] = "download_parameters"
        message["messageData"] = await sync_to_async(take_download_parameters)(event["message_text"])

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    #consumer updates
    async def update_connection_status(self, event):
        '''
        handle connection status update from group member
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info("Connection update")

#local sync functions
@sync_to_async
def get_session(id_):
    '''
    return session with specified id
    param: id_ {int} session id
    '''
    session = None
    logger = logging.getLogger(__name__)

    try:        
        session = Session.objects.get(id=id_)
        return session.json()
    except ObjectDoesNotExist:
        logger.warning(f"get_session session, not found: {id_}")
        return {}
        
def take_update_parameterset(data):
    '''
    update parameterset
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameters: {data}")

    session_id = data["sessionID"]
    form_data = data["formData"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameterset session, not found ID: {session_id}")
        return
    
    form_data_dict = form_data

    form = ParameterSetForm(form_data_dict, instance=session.parameter_set)

    if form.is_valid():
                  
        form.save()    

        session.parameter_set.update_parts_and_periods()

        return {"value" : "success"}                      
                                
    logger.info("Invalid paramterset form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_player(data):
    '''
    update parameterset player
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset player: {data}")

    session_id = data["sessionID"]
    paramterset_player_id = data["paramterset_player_id"]
    form_data = data["formData"]

    try:        
        parameter_set_player = ParameterSetPlayer.objects.get(id=paramterset_player_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_player parameterset_player, not found ID: {paramterset_player_id}")
        return
    
    form_data_dict = form_data

    # for field in form_data:            
    #     form_data_dict[field["name"]] = field["value"]

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetPlayerForm(form_data_dict, instance=parameter_set_player)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        return {"value" : "success"}                      
                                
    logger.info("Invalid parameterset player form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_player_part(data):
    '''
    update parameterset player part
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset player part: {data}")

    session_id = data["sessionID"]
    paramterset_player_part_id = data["paramterset_player_part_id"]
    form_data = data["formData"]

    try:        
        parameter_set_player_part = ParameterSetPlayerPart.objects.get(id=paramterset_player_part_id)
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_player_part paramterset_player_part_id, not found ID: {paramterset_player_part_id}")
        return
    
    form_data_dict = form_data
    form_data_dict['parameter_set_labels'] = form_data_dict['parameter_set_labels']['id']

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetPlayerPartForm(form_data_dict, instance=parameter_set_player_part)
    form.fields['parameter_set_labels'].queryset = session.parameter_set.parameter_set_labels.all()


    if form.is_valid():
        #print("valid form")             
        form.save()              

        return {"value" : "success",
                "result":{"indexes":data["indexes"],
                          "parameter_set_player_part":parameter_set_player_part.json()}}                      
                                
    logger.info("Invalid parameterset player part form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_remove_parameterset_player(data):
    '''
    remove the specifed parmeterset player
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Remove parameterset player: {data}")

    session_id = data["sessionID"]
    paramterset_player_id = data["paramterset_player_id"]

    try:        
        session = Session.objects.get(id=session_id)
        session.parameter_set.parameter_set_players.get(id=paramterset_player_id).delete()
        session.update_player_count()
    except ObjectDoesNotExist:
        logger.warning(f"take_remove_parameterset_player paramterset_player, not found ID: {paramterset_player_id}")
        return
    
    return {"value" : "success"}

def take_add_parameterset_player(data):
    '''
    add a new parameter player to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Add parameterset player: {data}")

    session_id = data["sessionID"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameterset session, not found ID: {session_id}")
        return

    session.parameter_set.add_new_player()

    session.update_player_count()

def take_update_parameterset_random_outcome(data):
    '''
    update parameterset random outcome
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset random outcome: {data}")

    session_id = data["sessionID"]
    paramterset_random_outcome_id = data["random_outcome_id"]
    form_data = data["formData"]

    try:        
        parameter_set_random_outcome = ParameterSetRandomOutcome.objects.get(id=paramterset_random_outcome_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_random_outcome random_outcome, not found ID: {paramterset_random_outcome_id}")
        return
    
    form_data_dict = form_data

    # for field in form_data:            
    #     form_data_dict[field["name"]] = field["value"]

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetRandomOutcomeForm(form_data_dict, instance=parameter_set_random_outcome)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        return {"value" : "success"}                      
                                
    logger.info("Invalid parameterset random outcome form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_add_paramterset_random_outcome(data):
    '''
    add a new parameter randome outcome to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Add parameterset random outcome: {data}")

    session_id = data["sessionID"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_add_paramterset_random_outcome session, not found ID: {session_id}")
        return

    ParameterSetRandomOutcome.objects.create(parameter_set=session.parameter_set)

def take_remove_parameterset_random_outcome(data):
    '''
    remove the specifed parmeterset random outcome
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Remove parameterset random outcome: {data}")

    session_id = data["sessionID"]
    random_outcome_id = data["random_outcome_id"]

    try:        
        session = Session.objects.get(id=session_id)
        session.parameter_set.parameter_set_random_outcomes.get(id=random_outcome_id).delete()
    except ObjectDoesNotExist:
        logger.warning(f"take_remove_parameterset_player paramterset_player, not found ID: {random_outcome_id}")
        return
    
    return {"value" : "success"}

def take_update_parameterset_part(data):
    '''
    update parameterset part
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset part: {data}")

    session_id = data["sessionID"]
    paramterset_part_id = data["paramterset_part_id"]
    form_data = data["formData"]

    try:        
        parameter_set_part = ParameterSetPart.objects.get(id=paramterset_part_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_player parameterset_player, not found ID: {paramterset_part_id}")
        return
    
    form_data_dict = form_data
    form_data_dict["instruction_set"] = form_data_dict["instruction_set"]["id"]

    # for field in form_data:            
    #     form_data_dict[field["name"]] = field["value"]

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetPartForm(form_data_dict, instance=parameter_set_part)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        return {"value" : "success"}                      
                                
    logger.info("Invalid parameterset part form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_part_period(data):
    '''
    update parameterset part period
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset part period: {data}")

    session_id = data["sessionID"]
    paramterset_part_period_id = data["paramterset_part_period_id"]
    form_data = data["formData"]

    try:        
        parameter_set_part_period = ParameterSetPartPeriod.objects.get(id=paramterset_part_period_id)
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_labels_period parameterset_labels_period, not found ID: {paramterset_part_period_id}")
        return
    
    form_data_dict = form_data
    form_data_dict['parameter_set_random_outcome'] = form_data_dict['parameter_set_random_outcome']['id']

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetPartPeriodForm(form_data_dict, instance=parameter_set_part_period)
    form.fields['parameter_set_random_outcome'].queryset =  session.parameter_set.parameter_set_random_outcomes.all()

    if form.is_valid():
        #print("valid form")             
        form.save()              

        return {"value" : "success",
                "result":{"indexes":data["indexes"],
                          "parameter_set_part_period":parameter_set_part_period.json()}}                      
                                
    logger.info("Invalid parameterset part period form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_randomize_part_periods(data):
    '''
    update parameterset randomize part periods
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset randomize part periods: {data}")

    session_id = data["sessionID"]

    try:        
        session = Session.objects.get(id=session_id)               
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_randomize_part_periods session, not found ID: {session_id}")
        return
    
    session.parameter_set.randomize_parts()
    
    return {"value" : "success"}

def take_update_parameterset_labels(data):
    '''
    update parameterset labels
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset labels: {data}")

    session_id = data["sessionID"]
    paramterset_labels_id = data["paramterset_labels_id"]
    form_data = data["formData"]

    try:        
        parameter_set_labels = ParameterSetLabels.objects.get(id=paramterset_labels_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_labels parameterset_label, not found ID: {paramterset_labels_id}")
        return
    
    form_data_dict = form_data

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetLabelsForm(form_data_dict, instance=parameter_set_labels)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        return {"value" : "success"}                      
                                
    logger.info("Invalid parameterset labels form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_labels_period(data):
    '''
    update parameterset labels period
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset labels period: {data}")

    session_id = data["sessionID"]
    parameterset_labels_period_id = data["parameterset_labels_period_id"]
    form_data = data["formData"]

    try:        
        parameter_set_labels_period = ParameterSetLabelsPeriod.objects.get(id=parameterset_labels_period_id)
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_labels_period parameterset_labels_period, not found ID: {parameterset_labels_period_id}")
        return
    
    form_data_dict = form_data
    form_data_dict['label'] = form_data_dict['label']['id']

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetLabelsPeriodForm(form_data_dict, instance=parameter_set_labels_period)
    form.fields['label'].queryset = session.parameter_set.parameter_set_random_outcomes.all()

    if form.is_valid():
        #print("valid form")             
        form.save()              

        parameter_set_labels_period = ParameterSetLabelsPeriod.objects.get(id=parameterset_labels_period_id)

        return {"value" : "success", 
                "result":{"indexes":data["indexes"],
                          "parameter_set_labels_period":parameter_set_labels_period.json()}}                      
                                
    logger.info("Invalid parameterset labels period form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_randomize_labels(data):
    '''
    update parameterset randomize labels
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset randomize labels: {data}")

    session_id = data["sessionID"]

    try:        
        session = Session.objects.get(id=session_id)               
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_randomize_labels session, not found ID: {session_id}")
        return
    
    session.parameter_set.randomize_labels()
    
    return {"value" : "success"}

def take_import_parameters(data):
    '''
    import parameters from another session
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Import parameters: {data}")

    session_id = data["sessionID"]
    form_data = data["formData"]
    
    form_data_dict = form_data

    if not form_data_dict["session"]:
        return {"status" : "fail", "message" :  "Invalid session."}

    # for field in form_data:            
    #     form_data_dict[field["name"]] = field["value"]

    source_session = Session.objects.get(id=form_data_dict["session"])
    target_session = Session.objects.get(id=session_id)

    status = target_session.parameter_set.from_dict(source_session.parameter_set.json()) 
    target_session.update_player_count()

    return status      

    # return {"value" : "fail" if "Failed" in message else "success",
    #         "message" : message}

def take_download_parameters(data):
    '''
    download parameters to a file
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Download parameters: {data}")

    session_id = data["sessionID"]

    session = Session.objects.get(id=session_id)
   
    return {"status" : "success", "parameter_set":session.parameter_set.json()}                      
