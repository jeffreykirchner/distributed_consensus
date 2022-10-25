'''
session player model
'''

#import logging
import uuid
import logging

from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.core.exceptions import ObjectDoesNotExist

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

    name = models.CharField(verbose_name='Full Name', max_length = 100, default="")                     #subject's full name
    student_id = models.CharField(verbose_name='Student ID', max_length = 100, default="")              #subject's student ID number
    email =  models.EmailField(verbose_name='Email Address', max_length = 100, blank=True, null=True)   #subject's email address
    earnings = models.IntegerField(verbose_name='Earnings in cents', default=0)                         #earnings in cents
    name_submitted = models.BooleanField(default=False, verbose_name='Name submitted')                  #true if subject has submitted name and student id

    current_instruction = models.IntegerField(verbose_name='Current Instruction', default=0)                     #current instruction page subject is on
    current_instruction_complete = models.IntegerField(verbose_name='Current Instruction Complete', default=0)   #furthest complete page subject has done
    instructions_finished = models.BooleanField(verbose_name='Instructions Finished', default=False)             #true once subject has completed instructions

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

        self.current_instruction = 1
        self.current_instruction_complete = 0
        self.instructions_finished = False

        self.session_player_parts_b.all().delete()
        self.session_player_chats_b.all().delete()

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

    def get_instruction_set(self):
        '''
        return a proccessed list of instructions to the subject
        '''

        instructions = [i.json() for i in self.parameter_set_player.parameter_set.instruction_set.instructions.all()]
 
        for i in instructions:
            i["text_html"] = i["text_html"].replace("#player_number#", self.parameter_set_player.id_label)
            i["text_html"] = i["text_html"].replace("#player_count-1#", str(self.parameter_set_player.parameter_set.parameter_set_players.count()-1))

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

            "earnings" : self.earnings,

            "player_number" : self.player_number,
            "player_key" : self.player_key,

            "login_link" : reverse('subject_home', kwargs={'player_key': self.player_key}),
            "connected_count" : self.connected_count,

            "parameter_set_player" : self.parameter_set_player.json(),
            "chat_all" : chat_all,
            
            "new_chat_message" : False,           #true on client side when a new un read message comes in

            "current_instruction" : self.current_instruction,
            "current_instruction_complete" : self.current_instruction_complete,
            "instructions_finished" : self.instructions_finished,

            "session_player_parts" : [p.json_for_subject() for p in self.session_player_parts_b.all()],

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
            "parameter_set_player" : self.parameter_set_player.json_for_subject(),

        }    
    

    def json_min(self):
        '''
        minimal json object of model
        '''

        return{
            "id" : self.id,    
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

        return f'${(self.earnings/100):.2f}'


        