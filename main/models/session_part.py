'''
session part model
'''

#import logging

from operator import truediv
from re import A
from tabnanny import verbose
from django.db import models
from main.globals.sessions import PartModes

from main.models import Session
from main.models import ParameterSetPart

import main

class SessionPart(models.Model):
    '''
    session part model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_parts_a")
    parameter_set_part = models.ForeignKey(ParameterSetPart, on_delete=models.CASCADE, related_name="session_parts_b", null=True, blank=True)

    current_session_part_period = models.ForeignKey('main.SessionPartPeriod', models.SET_NULL, blank=True, null=True, related_name="session_parts_c")

    show_results = models.BooleanField(default=False, verbose_name="Shown results to subject")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parameter_set_part}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'parameter_set_part'], name='unique_session_part')
        ]
        verbose_name = 'Session Part'
        verbose_name_plural = 'Session Parts'
        ordering = ['parameter_set_part']
    
    def setup(self):
        '''
        setup session part
        '''

        session_part_periods = []
        for p in self.parameter_set_part.parameter_set_part_periods_a.all():
            session_part_periods.append(main.models.SessionPartPeriod(session_part=self, parameter_set_part_period=p))
        
        main.models.SessionPartPeriod.objects.bulk_create(session_part_periods)

        self.current_session_part_period = self.session_part_periods_a.first()
        self.results_shown=False

        self.save()
        
    def advance_period(self):
        '''
        advance to next period
        '''

        if self.current_session_part_period.parameter_set_part_period.period_number==self.parameter_set_part.parameter_set.period_count:
            return False

        current_period_number = self.current_session_part_period.parameter_set_part_period.period_number

        self.current_session_part_period = self.session_part_periods_a.get(parameter_set_part_period__period_number=current_period_number+1)
        self.save()

        return True
    
    def calc_results(self):
        '''
        calculate results for this period
        '''
        if self.parameter_set_part.mode == main.globals.PartModes.A:
            for i in self.session_part_periods_a.all():
                i.paid = True
                i.save()

        for i in self.session_player_parts_a.all():
            i.calc_majority_choice()
            
    #return json object of class
    def json(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,
            "parameter_set_part" : self.parameter_set_part.json(),
        }
    
    def json_for_subject(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,
            "parameter_set_part" : self.parameter_set_part.json_for_subject(),
            "show_results" : self.show_results,
        }
        