'''
parameterset player 
'''

from django.db import models

from main.models import ParameterSet

import main

class ParameterSetPlayer(models.Model):
    '''
    session player parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_players")

    id_label = models.CharField(verbose_name='ID Label', max_length=2, default="1")      #id label shown on screen to subjects

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id_label}'

    class Meta:
        verbose_name = 'Parameter Set Player'
        verbose_name_plural = 'Parameter Set Players'
        ordering=['id_label']

    def from_dict(self, new_ps):
        '''
        copy source values into this period
        source : dict object of parameterset player
        '''

        self.id_label = new_ps.get("id_label")

        # parameter_set_player_parts
        new_parameter_set_player_parts = new_ps.get("parameter_set_player_parts")
        for index, p in enumerate(self.parameter_set_player_parts_a.all()):                
            p.from_dict(new_parameter_set_player_parts[index])

        self.save()
        
        message = "Parameters loaded successfully."

        return message
    
    def setup_parts(self):
        '''
        update the number player parts
        '''

        difference = self.parameter_set_player_parts_a.all().count() - self.parameter_set.part_count

        if difference>0:
            for i in range(difference):
                self.parameter_set_player_parts_a.last().delete()            
        elif difference<0:
            for i in range(abs(difference)):
                main.models.ParameterSetPlayerPart.objects.create(parameter_set_player=self)
        
        parameter_set_player_parts = list(self.parameter_set_player_parts_a.all())
        for index, i in enumerate(self.parameter_set.parameter_set_parts.all()):
            parameter_set_player_parts[index].parameter_set_part = i
            parameter_set_player_parts[index].save()

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,
            "id_label" : self.id_label,
            "parameter_set_player_parts" : [i.json() for i in self.parameter_set_player_parts_a.all()]
        }
    
    def json_for_subject(self):
        '''
        return json object for subject screen
        '''

        return{

            "id" : self.id,
            "id_label" : self.id_label,
            "parameter_set_player_parts" : [i.json() for i in self.parameter_set_player_parts_a.all()]

        }
    
    def json_min(self):
        '''
        small json model
        '''
        return{

            "id" : self.id,
            "id_label" : self.id_label,
        }


