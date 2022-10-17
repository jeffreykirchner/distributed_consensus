'''
session part period model
'''

#import logging

from django.db import models

from main.models import SessionPart
from main.models import ParameterSetPartPeriod

import main

class SessionPartPeriod(models.Model):
    '''
    session part period model
    '''
    session_part = models.ForeignKey(SessionPart, on_delete=models.CASCADE, related_name="session_part_periods_a")
    parameter_set_part_period = models.ForeignKey(ParameterSetPartPeriod, on_delete=models.CASCADE, related_name="session_part_periods_b", null=True, blank=True)

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
        