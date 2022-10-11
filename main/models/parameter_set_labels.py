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

class ParameterSetLabels(models.Model):
    '''
    parameter set part
    '''    
    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_labels")

    name = models.CharField(max_length = 1000, default="Name Here")

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Labels'
        verbose_name_plural = 'Parameter Set Labels'
        ordering=['name']
    
    def from_dict(self, new_ps):
        '''
        load values from dict
        '''
        logger = logging.getLogger(__name__) 

        message = "Parameters loaded successfully."
        status = "success"

        try:
            self.name = new_ps.get("name")
            
        except IntegrityError as exp:
            message = f"Failed to load parameter set labels: {exp}"
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
            "name" : self.name,
        }
    
    def json_for_subject(self):
        '''
        return json object for subject
        '''
        return{
            "id" : self.id,
            "name" : self.name,
        }
