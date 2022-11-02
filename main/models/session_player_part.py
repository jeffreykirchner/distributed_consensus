'''
session player part 
'''

import logging

from django.db import models
from django.db.models import Sum

from main.models import SessionPlayer
from main.models import SessionPart
from main.models import ParameterSetPlayerPart

import main

class SessionPlayerPart(models.Model):
    '''
    session player part model
    '''
    session_part = models.ForeignKey(SessionPart, on_delete=models.CASCADE, related_name="session_player_parts_a")
    session_player = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_parts_b")
    parameter_set_player_part = models.ForeignKey(ParameterSetPlayerPart, on_delete=models.CASCADE, related_name="session_player_parts_c", null=True, blank=True)

    earnings = models.IntegerField(verbose_name='Part Earnings', default=0)        #earnings in cents this period
    results_complete = models.BooleanField(default=False, verbose_name="Results Complete")

    current_instruction = models.IntegerField(verbose_name='Current Instruction', default=0)                     #current instruction page subject is on
    current_instruction_complete = models.IntegerField(verbose_name='Current Instruction Complete', default=0)   #furthest complete page subject has done
    instructions_finished = models.BooleanField(verbose_name='Instructions Finished', default=False)             #true once subject has completed instructions

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Player {self.session_player.parameter_set_player.id_label}, Part {self.session_part.parameter_set_part.part_number}"

    class Meta:
        
        verbose_name = 'Session Player Part'
        verbose_name_plural = 'Session Player Part'
        ordering = ['session_player', 'session_part']
        constraints = [
            models.UniqueConstraint(fields=['session_player', 'session_part'], name='unique_session_player_period'),
        ]
    
    def setup(self):
        '''
        setup player part
        '''

        session_player_part_periods = []

        for i in range(self.parameter_set_player_part.parameter_set_player.parameter_set.period_count):
            parameter_set_labels_period = self.parameter_set_player_part \
                                              .parameter_set_labels \
                                              .parameter_set_labels_period_a \
                                              .get(period_number=i+1)  
            
            session_part_period = self.session_part.session_part_periods_a.get(parameter_set_part_period__period_number=i+1)

            session_player_part_periods.append(main.models.SessionPlayerPartPeriod(session_player_part=self, \
                                                                                   parameter_set_labels_period=parameter_set_labels_period,
                                                                                   session_part_period=session_part_period))
        
        main.models.SessionPlayerPartPeriod.objects.bulk_create(session_player_part_periods)

    def write_summary_download_csv(self, writer):
        '''
        take csv writer and add row
        '''


        writer.writerow([self.session_period.session.id,
                         self.session_period.period_number,
                         self.session_player.player_number,
                         self.session_player.parameter_set_player.id_label,
                         self.earnings,])
    
    def get_current_session_player_part_period(self):
        '''
        return the current session player part period
        '''
        return self.session_player_part_periods_a.get(session_part_period=self.session_part.current_session_part_period)
    
    def calc_majority_choice(self):
        '''
        calc majority choice and earnings for this part
        '''
        logger = logging.getLogger(__name__)

        #calc majority choice for group
        for i in self.session_player_part_periods_a.all():
            i.calc_majority_choice()
        

        #mode A payment
        if self.session_part.parameter_set_part.mode == main.globals.PartModes.A:
            fail = False
            self.earnings = self.session_part.parameter_set_part.pay_choice_majority

            for i in self.session_player_part_periods_a.all():
                if i.majority_choice != i.choice:
                    fail = True
                    break

            if fail:
                self.earnings = self.session_part.parameter_set_part.pay_choice_minority

        #mode B payment
        elif self.session_part.parameter_set_part.mode == main.globals.PartModes.B:

            self.earnings = 0            
            for i in self.session_player_part_periods_a.filter(session_part_period__paid=True):
                if i.majority_choice == i.parameter_set_labels_period.label:
                    self.earnings += self.session_part.parameter_set_part.pay_label_majority
                else:
                    self.earnings += self.session_part.parameter_set_part.pay_label_minority

        #mode C payment
        elif self.session_part.parameter_set_part.mode == main.globals.PartModes.C:
            
            self.earnings = 0
            for i in self.session_player_part_periods_a.filter(session_part_period__paid=True):
                if i.majority_choice == i.parameter_set_labels_period.label:
                    self.earnings += self.session_part.parameter_set_part.pay_label_majority
                else:
                    self.earnings += self.session_part.parameter_set_part.pay_label_minority
                
                if i.majority_choice == i.choice:
                    self.earnings += self.session_part.parameter_set_part.pay_choice_majority
                else:
                    self.earnings += self.session_part.parameter_set_part.pay_choice_minority

        self.save()
        
        self.session_player.update_earnings()

    def get_group_number(self):
        '''
        return group number
        '''
        return self.parameter_set_player_part.group
    
    def get_group_members(self):
        '''
        return a list of SessionPlayerPartPeriod who in are this group
        '''

        return main.models.SessionPlayerPart.objects.filter(session_part=self.session_part) \
                                                    .filter(parameter_set_player_part__group=self.get_group_number())

    def json_for_subject(self):
        '''
        json object of model
        '''

        results = {}

        return{
            "id" : self.id,    
            "earnings" : f'{self.earnings:.2f}',
            "session_player_part_periods" : [i.json_for_subject() for i in self.session_player_part_periods_a.all()],
            "results_complete" : self.results_complete,
            "results" : results,
            "current_instruction" : self.current_instruction,
            "current_instruction_complete" : self.current_instruction_complete,
            "instructions_finished" : self.instructions_finished,
            "group_members" : [i.session_player.json_min() for i in self.get_group_members()],
            "mode" : self.session_part.parameter_set_part.mode,
            #"parameter_set_player_part" : self.parameter_set_player_part.json(),
        }