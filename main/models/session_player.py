'''
session player model
'''

#import logging
import uuid
import logging

from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder

from main.models import Session
from main.models import ParameterSetPlayer

from main.globals import round_half_away_from_zero

import main

class SessionPlayer(models.Model):
    '''
    session player model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_players_a")
    parameter_set_player = models.ForeignKey(ParameterSetPlayer, on_delete=models.CASCADE, related_name="session_players_b")

    player_number = models.IntegerField(verbose_name='Player number', default=0)                        #player number, from 1 to N
    player_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Player Key')      #login and channel key
    connecting = models.BooleanField(default=False, verbose_name='Consumer is connecting')              #true when a consumer is connceting
    connected_count = models.IntegerField(verbose_name='Number of consumer connections', default=0)     #number of consumers connected to this subject

    name = models.CharField(verbose_name='Full Name', max_length = 100, default="", blank=True, null=True)             #subject's full name
    student_id = models.CharField(verbose_name='Student ID', max_length = 100, default="", blank=True, null=True)      #subject's student ID number
    email =  models.EmailField(verbose_name='Email Address', max_length = 100, blank=True, null=True)                  #subject's email address
    earnings = models.IntegerField(verbose_name='Earnings in cents', default=0)                         #earnings in cents
    name_submitted = models.BooleanField(default=False, verbose_name='Name submitted')                  #true if subject has submitted name and student id

    session_player_parts_json = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)      #json model of player object
    parameter_set_player_json = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)      #json model of parameter_set_player

    survey_complete = models.BooleanField(default=False, verbose_name="Survey Complete")                 #subject has completed the survey  

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parameter_set_player.id_label}"

    class Meta:
        
        verbose_name = 'Session Player'
        verbose_name_plural = 'Session Players'
        ordering = ['player_number']
        constraints = [            
            models.UniqueConstraint(fields=['session', 'email'], name='unique_email_session_player', condition=~Q(email="")),
        ]

    def reset(self):
        '''
        reset player to starting state
        '''

        self.earnings = 0
        self.name = ""
        self.student_id = ""
        self.email = None
        self.name_submitted = False
        self.survey_complete = False

        self.current_instruction = 1
        self.current_instruction_complete = 0
        self.instructions_finished = False

        self.session_player_parts_b.all().delete()
        self.session_player_chats_b.all().delete()

        self.status_json = {}
        self.parameter_set_player_json = {}
        self.session_player_parts_json = {}

        self.save()
    
    def setup(self):
        '''
        setup player
        '''

        self.reset()

        #session player parts
        session_player_parts = []

        for p in self.parameter_set_player.parameter_set_player_parts_a.all():
            sp = self.session.session_parts_a.get(parameter_set_part=p.parameter_set_part)  

            session_player_parts.append(main.models.SessionPlayerPart(session_part=sp, \
                                                                      session_player=self, \
                                                                      parameter_set_player_part=p))
            
        main.models.SessionPlayerPart.objects.bulk_create(session_player_parts)

        for p in self.session_player_parts_b.all():
            p.setup()
        
        self.save() 
    
    def write_summary_download_csv(self, writer, session_data, part_index, period_index):
        '''
        take csv writer and add row
        '''
        # "Session", "Part", "Period", "Mode", "Image", "Paid", "Group", "Player", "Label Set", "Label", "Report", "Majority Reported"

        session_player_part = self.session_player_parts_json[part_index]
        session_player_part_period = session_player_part["session_player_part_periods"][period_index]

        parameter_set_player_part = self.parameter_set_player_json["parameter_set_player_parts"][part_index]

        out_data = session_data.copy()

        out_data.append(session_player_part_period["paid"])
        out_data.append(session_player_part_period["group_number"])
        out_data.append(self.parameter_set_player_json["id_label"])
        out_data.append(parameter_set_player_part["parameter_set_labels"]["name"])
        out_data.append(parameter_set_player_part["parameter_set_labels"]["parameter_set_labels_period"][period_index]["label"]["abbreviation"])
        out_data.append(session_player_part_period["choice"]["abbreviation"])

        if session_player_part_period["majority_choice"]:
            out_data.append(session_player_part_period["majority_choice"]["abbreviation"])
        else:
            out_data.append("None")

        writer.writerow(out_data)
    
    def update_json(self):
        '''
        update json objects
        '''

        self.session_player_parts_json = [p.json_for_subject() for p in self.session_player_parts_b.all()]
        self.parameter_set_player_json = self.parameter_set_player.json()  

        self.save()
        
    def update_earnings(self):
        '''
        update total earnings
        '''
        v = self.session_player_parts_b.all().aggregate(Sum('earnings'))
        self.earnings = v['earnings__sum']
        self.save()

    def get_instruction_set(self):
        '''
        return a proccessed list of instructions to the subject
        '''
        current_session_player_part = self.get_current_session_player_part()

        if not current_session_player_part:
            return []

        parameter_set = self.parameter_set_player.parameter_set
        parameter_set_part = current_session_player_part.session_part.parameter_set_part

        #outcome images
        outcome_image_html = "<div class='row'>"
        outcome_name_list = ""

        parameter_set_random_outcomes = parameter_set.parameter_set_random_outcomes.all()
        for index, i in enumerate(parameter_set_random_outcomes):
            outcome_image_html += "<div class='col-auto'>"
            outcome_image_html += f'<img src="/static/{i.image}" class="signal_image">'
            outcome_image_html += "</div>"

            if index==0:
                outcome_name_list = i.name
            elif parameter_set_random_outcomes.count()-1 == index:
                outcome_name_list += f' or {i.name}'
            else:
                outcome_name_list += f', {i.name}'

        outcome_image_html += "</div>"

        #group list
        group_list = ""
        group_memebers = current_session_player_part.get_group_members().all()
       
        for index, i in enumerate(group_memebers):
            id_label = f'Player {i.session_player.parameter_set_player_json["id_label"]}'
            if i.session_player==self:
                id_label += ' (You)'

            if index==0:
                group_list = f'{id_label}'
            elif group_memebers.count()-1 == index:
                group_list += f' and {id_label}'
            else:
                group_list += f', {id_label}'

        instructions = []
        for p in parameter_set.parameter_set_parts.all():
            instructions.append([i.json() for i in p.instruction_set.instructions.all()])
 
            for i in instructions[p.part_number-1]:
                
                i["text_html"] = i["text_html"].replace("#player_id_label#", self.parameter_set_player_json["id_label"])
                i["text_html"] = i["text_html"].replace("#number_of_players#", str(parameter_set.parameter_set_players.count()-1))
                
                i["text_html"] = i["text_html"].replace("#current_part#", str(parameter_set_part.part_number))
                i["text_html"] = i["text_html"].replace("#part_count#", str(parameter_set.part_count))
                i["text_html"] = i["text_html"].replace("#part_count-1#", str(parameter_set.part_count-1))
                i["text_html"] = i["text_html"].replace("#period_count#", str(parameter_set.period_count))

                i["text_html"] = i["text_html"].replace("#outcome_images#", outcome_image_html)
                i["text_html"] = i["text_html"].replace("#outcome_name_list#", outcome_name_list)

                i["text_html"] = i["text_html"].replace("#group_list#", group_list)

                i["text_html"] = i["text_html"].replace("#pay_choice_majority#", str(parameter_set_part.pay_choice_majority))
                i["text_html"] = i["text_html"].replace("#pay_choice_minority#", str(parameter_set_part.pay_choice_minority))
                i["text_html"] = i["text_html"].replace("#pay_label_majority#",  str(parameter_set_part.pay_label_majority))
                i["text_html"] = i["text_html"].replace("#pay_label_minority#",  str(parameter_set_part.pay_label_minority))

                i["text_html"] = i["text_html"].replace("#minimum_for_majority-1#",  str(parameter_set_part.minimum_for_majority-1))
                
        return instructions
    
    def get_current_session_player_part(self):
        '''
        return the current session player part
        '''
        return self.session_player_parts_b.get(session_part=self.session.current_session_part) if self.session.started else None

    def json(self, get_chat=True):
        '''
        json object of model
        '''
        # "chat_all" : [c.json_for_subject() for c in self.session_player_chats_c.filter(chat_type=main.globals.ChatTypes.ALL)
            #                                                                        .order_by('-timestamp')[:100:-1]
            #              ] if get_chat else [],
        chat_all = []

        return{
            "id" : self.id,      
            "name" : self.name,
            "student_id" : self.student_id,   
            "email" : self.email,
            "name_submitted" : self.name_submitted,

            "earnings" : f'{self.earnings:.2f}',

            "player_number" : self.player_number,
            "player_key" : self.player_key,

            "login_link" : reverse('subject_home', kwargs={'player_key': self.player_key}),
            "connected_count" : self.connected_count,

            "parameter_set_player" : self.parameter_set_player_json if self.session.started else self.parameter_set_player.json(), 
            "chat_all" : chat_all,
            
            "new_chat_message" : False,           #true on client side when a new un read message comes in

            "survey_complete" : self.survey_complete,

            "session_player_parts" : self.session_player_parts_json if self.session.started else [p.json_for_subject() for p in self.session_player_parts_b.all()],
        }
    
    def json_for_staff_session(self):
        '''
        get json object for staff home screen
        '''

        return{
            "id" : self.id,      
            "name" : self.name,
            "student_id" : self.student_id,   
            "email" : self.email,
            "name_submitted" : self.name_submitted,

            "earnings" : f'{self.earnings:.2f}',

            "player_number" : self.player_number,
            "player_key" : self.player_key,

            "login_link" : reverse('subject_home', kwargs={'player_key': self.player_key}),
            "connected_count" : self.connected_count,

            "survey_complete" : self.survey_complete,

            "parameter_set_player" : self.parameter_set_player_json if self.session.started else self.parameter_set_player.json(),      
            "session_player_parts" : self.session_player_parts_json if self.session.started else [p.json_for_subject() for p in self.session_player_parts_b.all()],  
        }
    
    
    def json_for_subject(self, session_player):
        '''
        json model for subject screen
        session_player_id : int : id number of session player for induvidual chat
        '''

         # "chat_individual" : [c.json_for_subject() for c in  main.models.SessionPlayerChat.objects \
            #                                                                 .filter(chat_type=main.globals.ChatTypes.INDIVIDUAL) \
            #                                                                 .filter(Q(Q(session_player_recipients=session_player) & Q(session_player=self)) |
            #                                                                         Q(Q(session_player_recipients=self) & Q(session_player=session_player)))
            #                                                                 .order_by('-timestamp')[:100:-1]
            #                     ],
        chat_individual = []

        return{
            "id" : self.id,  
            "player_number" : self.player_number,
            "chat_individual" : chat_individual,
            "new_chat_message" : False,           #true on client side when a new un read message comes in
            "parameter_set_player" : self.parameter_set_player_json,
        }    
    

    def json_min(self):
        '''
        minimal json object of model
        '''

        return{
            "id" : self.id,    
            "player_number" : self.player_number,
            "id_label" : self.parameter_set_player.id_label,
        }
    
    def json_current_choice(self):
        '''
        json for current choice
        '''

        if not self.session.started:
            return {"id" : self.id,}

        session_player_part = self.get_current_session_player_part()

        session_player_part_period = session_player_part.get_current_session_player_part_period()

        return{
            "id" : self.id,    

            #"session_player_part" : session_player_part.json_for_subject(),
            "session_player_part_period" : session_player_part_period.json_for_subject(),            
            "session_part" : self.session.current_session_part.json_for_subject(), 
            "session_part_period" : self.session.current_session_part.current_session_part_period.json_for_subject(),   
            "session_player_part_period_group" : session_player_part_period.get_group_labels(),    
        }
    
    def json_earning(self):
        '''
        return json object of earnings only
        '''
        return{
            "id" : self.id, 
            "earnings" : self.earnings,
        }
    
    def get_earnings_in_dollars(self):
        '''
        return earnings in dollar format
        '''

        return f'${(self.earnings):.2f}'


        