'''
parameter set
'''
import logging

from django.db import models
from django.db.utils import IntegrityError

from main.models import ParameterSet

from django.forms.models import model_to_dict

import main

class ParameterSetRandomOutcome(models.Model):
    '''
    parameter set part
    '''    
    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_random_outcomes")
    
    name = models.CharField(max_length=100, default="Name Here")
    abbreviation = models.CharField(max_length=10, default="NH")
    image = models.CharField(max_length=100, default="abc.jpg")

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.abbreviation})'

    class Meta:
        verbose_name = 'Parameter Set Random Outcome'
        verbose_name_plural = 'Parameter Set Random Outcomes'
        ordering=['name']
    
    def from_dict(self, new_ps):
        '''
        load values from dict
        '''
        logger = logging.getLogger(__name__) 

        try:
            self.name = new_ps.get("name")
            self.abbreviation = new_ps.get("abbreviation")
            self.image = new_ps.get("image")
            
            self.save()
        except IntegrityError as exp:
            message = f"Failed to load parameter set part: {exp}"
            status = "fail"
            logger.warning(message)

        self.save()

        message = "Parameters loaded successfully."
        status = "success"

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
        return model_to_dict(self)
        
        return{
            "id" : self.id,
            "name" : self.name,
            "abbreviation" : self.abbreviation, 
            "image" : self.image,           
        }
    
    def json_for_subject(self):
        '''
        return json object for subject
        '''
        return model_to_dict(self)

        return{
            "id" : self.id,
            "name" : self.name,
            "abbreviation" : self.abbreviation,
            "image" : self.image,   
        }

