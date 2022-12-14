'''
parameterset player 
'''

from django.db import models

from main.models import ParameterSetPlayer
from main.models import ParameterSetPart
from main.models import ParameterSetLabels

import main
from main.models.parameter_set_labels import ParameterSetLabels

class ParameterSetPlayerPart(models.Model):
    '''
    session player part parameters 
    '''

    parameter_set_player = models.ForeignKey(ParameterSetPlayer, on_delete=models.CASCADE, related_name="parameter_set_player_parts_a")
    parameter_set_part = models.ForeignKey(ParameterSetPart, models.SET_NULL, related_name="parameter_set_player_parts_b", blank=True, null=True)
    parameter_set_labels = models.ForeignKey(ParameterSetLabels, models.SET_NULL, related_name="parameter_set_player_parts_c", blank=True, null=True)

    group = models.IntegerField(verbose_name='Group Number', default=0)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Part {self.parameter_set_part.part_number}'

    class Meta:
        verbose_name = 'Parameter Set Player Part'
        verbose_name_plural = 'Parameter Set Player Parts'
        ordering=['parameter_set_part']

    def from_dict(self, new_ps):
        '''
        copy source values into this period
        source : dict object of parameterset player
        '''

        self.group = new_ps.get('group')

        self.parameter_set_part = self.parameter_set_player \
                                    .parameter_set \
                                    .parameter_set_parts\
                                    .filter(part_number=new_ps.get("parameter_set_part")["part_number"]).first()

        if new_ps.get("parameter_set_labels").get("id", None):
            self.parameter_set_labels = self.parameter_set_player \
                                        .parameter_set \
                                        .parameter_set_labels\
                                        .filter(name=new_ps.get("parameter_set_labels")["name"]).first()

        self.save()
        
        message = "Parameters loaded successfully."

        return message
    
    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,        
            "group" : self.group,    
            "parameter_set_part" : self.parameter_set_part.json() if self.parameter_set_part else None,
            "parameter_set_labels" : self.parameter_set_labels.json() if self.parameter_set_labels else {'id':None},
        }
    
    def json_for_subject(self):
        '''
        return json object for subject screen
        '''

        return{

            "id" : self.id,
            "group" : self.group,
            "parameter_set_part" : self.parameter_set_part.json() if self.parameter_set_part else None,
            "parameter_set_labels" : self.parameter_set_labels.json() if self.parameter_set_labels else {'id':None},
        }


