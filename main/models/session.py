'''
session model
'''

from datetime import datetime
from tinymce.models import HTMLField
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import logging
import uuid
import csv
import io

from django.conf import settings

from django.dispatch import receiver
from django.db import models
from django.db import transaction
from django.db.models.signals import post_delete
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder

import main

from main.models import ParameterSet

from main.globals import ExperimentPhase
from main.globals import PartModes

#experiment sessoin
class Session(models.Model):
    '''
    session model
    '''
    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions_a")
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="sessions_b")
    current_session_part = models.ForeignKey('main.SessionPart', models.SET_NULL, blank=True, null=True, related_name="sessions_c")

    title = models.CharField(max_length = 300, default="*** New Session ***")    #title of session
    start_date = models.DateField(default=now)                                   #date of session start

    current_experiment_phase = models.CharField(max_length=100, choices=ExperimentPhase.choices, default=ExperimentPhase.RUN)         #current phase of expeirment

    channel_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Channel Key')     #unique channel to communicate on
    session_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Session Key')     #unique key for session to auto login subjects by id

    started =  models.BooleanField(default=False)                                #starts session and filll in session    
    time_remaining = models.IntegerField(default=0)                              #time remaining in current phase of current period
    timer_running = models.BooleanField(default=False)                           #true when period timer is running
    finished = models.BooleanField(default=False)                                #true after all session periods are complete

    shared = models.BooleanField(default=False)                                  #shared session parameter sets can be imported by other users
    locked = models.BooleanField(default=False)                                  #locked models cannot be deleted

    invitation_text = HTMLField(default="", verbose_name="Invitation Text")       #inviataion email subject and text
    invitation_subject = HTMLField(default="", verbose_name="Invitation Subject")

    soft_delete =  models.BooleanField(default=False)                            #hide session if true

    parameter_set_json = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)                  #json model of parameter_set
    parameter_set_json_for_subject = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)      #json model of parameter_set for subject

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def creator_string(self):
        return self.creator.email
    creator_string.short_description = 'Creator'

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        ordering = ['-start_date']

    def get_start_date_string(self):
        '''
        get a formatted string of start date
        '''
        return  self.start_date.strftime("%#m/%#d/%Y")
    
    def get_group_channel_name(self):
        '''
        return channel name for group
        '''
        page_key = f"session-{self.id}"
        room_name = f"{self.channel_key}"
        return  f'{page_key}-{room_name}'
    
    def send_message_to_group(self, message_type, message_data):
        '''
        send socket message to group
        '''
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(self.get_group_channel_name(),
                                                {"type" : message_type,
                                                 "data" : message_data})

    def start_experiment(self):
        '''
        setup and start experiment
        '''
        logger = logging.getLogger(__name__)

        start_time = datetime.now()

        self.reset_experiment()

        self.started = True
        self.finished = False
        self.current_period = 1
        self.start_date = datetime.now()
        self.time_remaining = self.parameter_set.period_length

        if self.parameter_set.show_instructions:
            self.current_experiment_phase = ExperimentPhase.INSTRUCTIONS
        else:
            self.current_experiment_phase = ExperimentPhase.RUN

        self.parameter_set_json = self.parameter_set.json()
        self.parameter_set_json_for_subject = self.parameter_set.json_for_subject()

        #create parts
        session_parts = []
        for p in self.parameter_set.parameter_set_parts.all():
            session_parts.append(main.models.SessionPart(session=self, parameter_set_part=p))
        
        main.models.SessionPart.objects.bulk_create(session_parts)

        for p in self.session_parts_a.all():
            p.setup()

        self.save()

        #setup players
        for i in self.session_players_a.all():
            i.setup()

        for i in self.session_players_a.all():
            i.update_json()
            
        #set current part
        self.current_session_part = self.session_parts_a.first()

        self.save()

        logger.info(f'Start length: {datetime.now() - start_time}')
 
    def reset_experiment(self):
        '''
        reset the experiment
        '''
        self.started = False
        self.finished = False
        self.current_period = 1
        self.time_remaining = self.parameter_set.period_length
        self.timer_running = False
        self.current_experiment_phase = ExperimentPhase.RUN
        self.parameter_set_json = {}
        self.parameter_set_json_for_subject = {}

        self.save()

        for p in self.session_players_a.all():
            p.reset()
        
        self.session_parts_a.all().delete()
    
    def reset_connection_counts(self):
        '''
        reset connection counts
        '''
        self.session_players_a.all().update(connecting=False, connected_count=0)
    
    def update_player_count(self):
        '''
        update the number of session players based on the number defined in the parameterset
        '''

        self.session_players_a.all().delete()
    
        for count, i in enumerate(self.parameter_set.parameter_set_players.all()):
            new_session_player = main.models.SessionPlayer()

            new_session_player.session = self
            new_session_player.parameter_set_player = i
            new_session_player.player_number = count + 1

            new_session_player.save()

    def do_period_timer(self):
        '''
        do period timer actions
        '''

        status = "success"
        end_game = False

        #check session over
        if self.time_remaining == 0 and \
           self.current_period >= self.parameter_set.period_count:

            self.finished = True
            end_game = True


        if not status == "fail" and not end_game:

            if self.time_remaining == 0:
               
                self.current_period += 1
                self.time_remaining = self.parameter_set.period_length
        
            else:                                     

                self.time_remaining -= 1

        self.save()

        result = self.json_for_timer()

        return {"value" : status,
                "result" : result,
                "end_game" : end_game}

    def check_advance_period(self):
        '''
        check if all subjects have submitted their choices.
        '''
        logger = logging.getLogger(__name__)
        
        with transaction.atomic():
            v = main.models.SessionPlayerPartPeriod.objects.filter(choice=None)\
                                                           .filter(session_part_period=self.current_session_part.current_session_part_period)\

            #logger.info(v)                                                

        if v.count() > 0:
            return None
        else:
            if self.current_session_part.advance_period():
                return self.get_current_session_part_and_period_index()
            elif self.advance_part():
                return self.get_current_session_part_and_period_index()                     

    def advance_part(self):
        '''
        advance to the next session part
        '''
        #check that if part A show results
        if self.current_session_part.parameter_set_part.mode == PartModes.A:

            if not self.current_session_part.show_results:
                
                with transaction.atomic():
                    self.current_session_part.show_results = True
                    self.current_session_part.save()

                    self.current_session_part.session_player_parts_a.all().update(results_complete=False)

                #calc and send Part A results
                self.current_session_part.calc_results()

                self.send_message_to_group("update_current_session_part_result", {})
                
                return True
            else:

                c = self.current_session_part.session_player_parts_a.filter(results_complete=False).count()

                if c > 0:
                    return False

        #check end game
        if self.current_session_part.parameter_set_part.part_number==self.parameter_set.part_count:
            self.current_experiment_phase = ExperimentPhase.PAY
            self.save()
            return True         

        current_part_number = self.current_session_part.parameter_set_part.part_number

        self.current_session_part = self.session_parts_a.get(parameter_set_part__part_number=current_part_number+1)
       
        #check show instructions
        if self.parameter_set.show_instructions:
            self.current_experiment_phase = ExperimentPhase.INSTRUCTIONS

        self.save()

        return True

    def get_download_summary_csv(self):
        '''
        return data summary in csv format
        '''
        v = ["Session", "Part", "Period", "Mode", "Image", "Paid", "Group", "Player", "Label Set", "Label", "Report", "Report Length (ms)", "Majority Reported"]
        for i in self.parameter_set.parameter_set_random_outcomes.all():
            v.append(f'{i.name} Report Count')

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(v)

        for index_i, i in enumerate(self.parameter_set_json["parameter_set_parts"]):

            for index_j, j in enumerate(i["parameter_set_part_periods"]):

                session_data = [self.id, 
                                index_i + 1,
                                index_j + 1,
                                i["mode"],
                                j["parameter_set_random_outcome"]["abbreviation"]]

                for index_k, k in enumerate(self.session_players_a.all()):
                    k.write_summary_download_csv(writer, session_data, index_i, index_j) 

        # for p in session_player_periods.all():
        #     p.write_summary_download_csv(writer)

        return output.getvalue()
    
    def get_download_action_csv(self):
        '''
        return data actions in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(["Session ID", "Period", "Time", "Client #", "Label", "Action", "Info", "Info (JSON)", "Timestamp"])

        session_player_chats = main.models.SessionPlayerChat.objects.filter(session_player__in=self.session_players_a.all())

        for p in session_player_chats.all():
            p.write_action_download_csv(writer)

        return output.getvalue()
    
    def get_download_recruiter_csv(self):
        '''
        return data recruiter in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output)

        session_players = self.session_players_a.all()

        for p in session_players:
            writer.writerow([p.student_id, p.earnings])

        return output.getvalue()
    
    def get_download_payment_csv(self):
        '''
        return data payments in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output)

        writer.writerow(['Name', 'Student ID', 'Earnings'])

        session_players = self.session_players_a.all()

        for p in session_players:
            writer.writerow([p.name, p.student_id, p.earnings])

        return output.getvalue()

    def get_current_session_part_and_period_index(self):
        '''
        return the array index of the current session part
        '''

        part_index = -1
        period_index = -1

        if self.current_session_part: 
            part_index = self.current_session_part.parameter_set_part.part_number-1
            period_index = self.current_session_part.current_session_part_period.parameter_set_part_period.period_number-1
         
        return {"part_index" : part_index, 
                "period_index" : period_index,
               }

    def json(self):
        '''
        return json object of model
        '''
              
        # chat_all = [c.json_for_staff() for c in main.models.SessionPlayerChat.objects \
        #                                             .filter(session_player__in=self.session_players_a.all())\
        #                                             .prefetch_related('session_player_recipients')
        #                                             .select_related('session_player__parameter_set_player')
        #                                             .order_by('-timestamp')[:100:-1]
        #        ]                                                           
       
        chat_all = []
        return{
            "id":self.id,
            "title":self.title,
            "locked":self.locked,
            "start_date":self.get_start_date_string(),
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
            "parameter_set": self.parameter_set_json if self.started else self.parameter_set.json(),
            "session_parts":[i.json() for i in self.session_parts_a.all()],
            "session_players":[i.json(False) for i in self.session_players_a.all()],
            "chat_all" : chat_all,
            "invitation_text" : self.invitation_text,
            "invitation_subject" : self.invitation_subject,
            "current_index" : self.get_current_session_part_and_period_index(),
        }
    
    def json_min(self):
        '''
        small json model
        '''
        return{
            "id":self.id,
            "title":self.title,
            "locked":self.locked,
            "start_date":self.get_start_date_string(),
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
            "parameter_set": self. self.parameter_set_json if self.started else self.parameter_set.json(),
            "session_parts":[i.json() for i in self.session_parts_a.all()],
            "session_players":[i.json(False) for i in self.session_players_a.all()],
            "invitation_text" : self.invitation_text,
            "invitation_subject" : self.invitation_subject,
            "current_index" : self.get_current_session_part_and_period_index(),
        }
    
    def json_for_staff_session(self):
        '''
        small json model
        '''
        return{
            "id":self.id,
            "title":self.title,
            "locked":self.locked,
            "start_date":self.get_start_date_string(),
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
            "parameter_set": self.parameter_set_json if self.started else self.parameter_set.json(),
            "session_parts":[i.json() for i in self.session_parts_a.all()],
            "session_players":[i.json_for_staff_session() for i in self.session_players_a.all()],
            "invitation_text" : self.invitation_text,
            "invitation_subject" : self.invitation_subject,
            "current_index" : self.get_current_session_part_and_period_index(),
        }
    
    def json_for_subject(self, session_player):
        '''
        json object for subject screen
        session_player : SessionPlayer() : session player requesting session object
        '''
        
        return{
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
            "parameter_set":self.parameter_set_json_for_subject if self.started else self.parameter_set.json_for_subject(),

            "current_index" : self.get_current_session_part_and_period_index(),

            #"session_players":[i.json_for_subject(session_player) for i in session_player.session.session_players_a.all()]
        }
    
    def json_for_timer(self):
        '''
        return json object for timer update
        '''

        session_players = []

        return{
            "started":self.started,
            "current_period":self.current_period,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
            "session_players":session_players,
            "session_player_earnings": [i.json_earning() for i in self.session_players_a.all()]
        }
        
@receiver(post_delete, sender=Session)
def post_delete_parameterset(sender, instance, *args, **kwargs):
    '''
    use signal to delete associated parameter set
    '''
    if instance.parameter_set:
        instance.parameter_set.delete()
