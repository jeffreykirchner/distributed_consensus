'''
parameter set
'''
import logging

from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError

from main.globals import PartModes

from main.models import ParameterSet

import main

class ParameterSetPart(models.Model):
    '''
    parameter set part
    '''    
    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_parts")
    mode = models.CharField(max_length=100, choices=PartModes.choices, default=PartModes.A)
    part_number = models.IntegerField(verbose_name='Part Number', default=0)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Part'
        verbose_name_plural = 'Parameter Set Parts'
        ordering=['part_number']
    
    def from_dict(self, new_ps):
        '''
        load values from dict
        '''
        logger = logging.getLogger(__name__) 

        message = "Parameters loaded successfully."
        status = "success"

        try:
            self.mode = new_ps.get("mode")
            self.part_number = new_ps.get("part_number")
            
        except IntegrityError as exp:
            message = f"Failed to load parameter set part: {exp}"
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
            "mode" : self.mode,
            "part_number" : self.part_number,
        }
    
    def json_for_subject(self):
        '''
        return json object for subject
        '''
        return{
            "id" : self.id,
            "mode" : self.mode,
            "part_number" : self.part_number,
        }

