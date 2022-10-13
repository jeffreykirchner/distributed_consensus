'''
parameter set
'''
import logging

from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError

from main.globals import PartModes

from main.models import ParameterSetPart
from main.models import ParameterSetRandomOutcome

import main

class ParameterSetPartPeriod(models.Model):
    '''
    parameter set part period
    '''    
    parameter_set_part = models.ForeignKey(ParameterSetPart, on_delete=models.CASCADE, related_name="parameter_set_part_periods_a")
    parameter_set_random_outcome = models.ForeignKey(ParameterSetRandomOutcome, models.SET_NULL, related_name="parameter_set_part_periods_b", null=True, blank=True)

    period_number = models.IntegerField(verbose_name='Period Number', default=0)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Part Period'
        verbose_name_plural = 'Parameter Part Periods'
        ordering=['period_number']
    
    def from_dict(self, new_ps):
        '''
        load values from dict
        '''
        logger = logging.getLogger(__name__) 

        message = "Parameters loaded successfully."
        status = "success"

        try:
            self.period_number = new_ps.get("period_number")

            self.parameter_set_random_outcome = self.parameter_set_part \
                                                    .parameter_set \
                                                    .parameter_set_random_outcomes \
                                                    .filter(name=new_ps.get("label")["name"]).first()
            
            self.save()
        except IntegrityError as exp:
            message = f"Failed to load parameter set part period: {exp}"
            status = "fail"
            logger.warning(message)

        return {"status" : status, "message" :  message}

    def setup(self):
        '''
        default setup
        '''    
        pass

    def json(self):
        '''
        return json object of model
        '''
        return{
            "id" : self.id,
            "period_number" : self.period_number,
            "parameter_set_random_outcome" : self.label.json() if self.label else {'id':None},
        }
    
    def json_for_subject(self):
        '''
        return json object for subject
        '''
        return{
            "id" : self.id,
            "period_number" : self.period_number,
            "parameter_set_random_outcome" : self.label.json() if self.label else {'id':None},
        }

