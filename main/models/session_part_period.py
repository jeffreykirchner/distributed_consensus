'''
session part period model
'''

#import logging

from django.db import models

from main.models import SessionPart
from main.models import ParameterSetPartPeriod
from main.models import ParameterSetRandomOutcome

import main

class SessionPartPeriod(models.Model):
    '''
    session part period model
    '''
    session_part = models.ForeignKey(SessionPart, on_delete=models.CASCADE, related_name="session_part_periods_a")
    parameter_set_part_period = models.ForeignKey(ParameterSetPartPeriod, on_delete=models.CASCADE, related_name="session_part_periods_b", null=True, blank=True)
    
    paid = models.BooleanField(default=False, verbose_name='Pay subjects for this period')              #true if subjects are paid for this period

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session_part', 'parameter_set_part_period'], name='unique_session_part_period')
        ]
        verbose_name = 'Session Part Period'
        verbose_name_plural = 'Session Periods'
        ordering = ['session_part', 'parameter_set_part_period']

    #return json object of class
    def json(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,
            #"parameter_set_part_period" : self.parameter_set_part_period.json(),
        }
    
    def json_for_subject(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,
            "parameter_set_part_period" : self.parameter_set_part_period.json_for_subject(),       
            "paid" : self.paid,     
        }
        