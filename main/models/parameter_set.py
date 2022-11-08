'''
parameter set
'''
import logging

from django.db import models
from django.db.utils import IntegrityError

from main import globals

import main

class ParameterSet(models.Model):
    '''
    parameter set
    '''    
    part_count = models.IntegerField(verbose_name='Number or parts.', default=3)                              #number of parts in the experiment
    period_count = models.IntegerField(verbose_name='Number of periods per part.', default=10)                #number of periods in each part of the experiment
    period_length = models.IntegerField(verbose_name='Period Length, Production', default=10)                 #period length in seconds
    label_set_count = models.IntegerField(verbose_name='Number or label sets.', default=3)  

    private_chat = models.BooleanField(default=True, verbose_name='Private Chat')                           #if true subjects can privately chat one on one
    show_instructions = models.BooleanField(default=True, verbose_name='Show Instructions')                 #if true show instructions

    test_mode = models.BooleanField(default=False, verbose_name='Test Mode')                                #if true subject screens will do random auto testing

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set'
        verbose_name_plural = 'Parameter Sets'
    
    def from_dict(self, new_ps):
        '''
        load values from dict
        '''
        logger = logging.getLogger(__name__) 

        message = "Parameters loaded successfully."
        status = "success"

        try:
            self.part_count = new_ps.get("part_count")
            self.period_count = new_ps.get("period_count")
            self.period_length = new_ps.get("period_length")
            self.label_set_count = new_ps.get("label_set_count")

            self.private_chat = new_ps.get("private_chat")
            self.show_instructions = new_ps.get("show_instructions")

            self.save()
            
            #create parameter set players
            new_parameter_set_players = new_ps.get("parameter_set_players")

            if len(new_parameter_set_players) > self.parameter_set_players.count():
                #add more players
                new_player_count = len(new_parameter_set_players) - self.parameter_set_players.count()

                for i in range(new_player_count):
                     main.models.ParameterSetPlayer.objects.create(parameter_set=self)

            elif len(new_parameter_set_players) < self.parameter_set_players.count():
                #remove excess players

                extra_player_count = self.parameter_set_players.count() - len(new_parameter_set_players)

                for i in range(extra_player_count):
                    self.parameter_set_players.last().delete()
            
            #random outcomes
            new_parameter_set_random_outcomes = new_ps.get("parameter_set_random_outcomes")
            if len(new_parameter_set_random_outcomes) > self.parameter_set_random_outcomes.count():
                #add more players
                new_count = len(new_parameter_set_random_outcomes) - self.parameter_set_random_outcomes.count()

                for i in range(new_count):
                    main.models.ParameterSetRandomOutcome.objects.create(parameter_set=self)

            elif len(new_parameter_set_random_outcomes) < self.parameter_set_random_outcomes.count():
                #remove excess players

                extra_count = self.parameter_set_random_outcomes.count() - len(new_parameter_set_random_outcomes)

                for i in range(extra_count):
                    self.parameter_set_random_outcomes.last().delete()
            
            self.update_parts_and_periods()

            #load random outcomes
            new_parameter_set_random_outcomes = new_ps.get("parameter_set_random_outcomes")
            for index, p in enumerate(self.parameter_set_random_outcomes.all()):                
                p.from_dict(new_parameter_set_random_outcomes[index])

            #load labels
            new_parameter_set_labels = new_ps.get("parameter_set_labels")
            for index, p in enumerate(self.parameter_set_labels.all()):                
                p.from_dict(new_parameter_set_labels[index])

            #load parts
            new_parameter_set_parts = new_ps.get("parameter_set_parts")
            for index, p in enumerate(self.parameter_set_parts.all()):                
                p.from_dict(new_parameter_set_parts[index])

            #load players
            new_parameter_set_players = new_ps.get("parameter_set_players")
            for index, p in enumerate(self.parameter_set_players.all()):                
                p.from_dict(new_parameter_set_players[index])
            
        except IntegrityError as exp:
            message = f"Failed to load parameter set: {exp}"
            status = "fail"
            logger.warning(message)

        return {"status" : status, "message" :  message}

    def setup(self):
        '''
        default setup
        '''    
        pass

    def update_parts_and_periods(self):
        '''
        add or remove associated tables based on the number of parts and periods
        '''

        #remove excess parts
        self.parameter_set_parts.filter(part_number__gt=self.part_count).delete()

        for i in range(self.part_count):
           v = main.models.ParameterSetPart.objects.filter(parameter_set=self,                                                                             
                                                           part_number=i+1).first()
           if not v:
                main.models.ParameterSetPart.objects.create(parameter_set=self,
                                                            instruction_set=main.models.InstructionSet.objects.first(),
                                                            part_number=i+1) 
                                                                            
        #add remove label set
        difference = self.parameter_set_labels.all().count() - self.label_set_count
        if difference>0:
            for i in range(difference):
                self.parameter_set_labels.last().delete()            
        elif difference<0:
            for i in range(abs(difference)):
                main.models.ParameterSetLabels.objects.create(parameter_set=self)
        
        for i in self.parameter_set_labels.all():
            i.update_labels_periods_count()             
        
        #setup players
        for i in self.parameter_set_players.all():
            i.setup_parts()

        #setup parts
        for i in self.parameter_set_parts.all():
            i.setup_periods()

    def add_new_player(self):
        '''
        add a new player of type subject_type
        '''

        player = main.models.ParameterSetPlayer()
        player.parameter_set = self

        player.save()
        player.setup_parts()
    
    def randomize_labels(self):
        '''
        randomize labels
        '''

        for i in self.parameter_set_labels.all():
            i.randomize()
    
    def randomize_parts(self):
        '''
        randomize parts
        '''

        for i in self.parameter_set_parts.all():
            i.randomize()

    def json(self):
        '''
        return json object of model
        '''
        return{
            "id" : self.id,

            "part_count" : self.part_count,
            "period_count" : self.period_count,
            "period_length" : self.period_length,
            "label_set_count" : self.label_set_count,

            "private_chat" : "True" if self.private_chat else "False",
            "show_instructions" : "True" if self.show_instructions else "False",

            "parameter_set_players" : [p.json() for p in self.parameter_set_players.all()],
            "parameter_set_parts" : [p.json() for p in self.parameter_set_parts.all()],
            "parameter_set_labels" : [p.json() for p in self.parameter_set_labels.all()],
            "parameter_set_random_outcomes" : [p.json() for p in self.parameter_set_random_outcomes.all()],

            "test_mode" : "True" if self.test_mode else "False",
        }
    
    def json_min(self):
        '''
        small json model
        '''
        return {
            "id" : self.id,

            "part_count" : self.part_count,
            "period_count" : self.period_count,
            "period_length" : self.period_length,
            "label_set_count" : self.label_set_count,

            "private_chat" : "True" if self.private_chat else "False",
            "show_instructions" : "True" if self.show_instructions else "False",          
        }

    
    def json_for_subject(self):
        '''
        return json object for subject
        '''
        return{
            "id" : self.id,

            "part_count" : self.part_count,
            "period_count" : self.period_count,
            "period_length" : self.period_length,
            "label_set_count" : self.label_set_count,

            "show_instructions" : "True" if self.show_instructions else "False",
            "private_chat" : self.private_chat,

            "test_mode" : self.test_mode,

            "parameter_set_random_outcomes" : [p.json_for_subject() for p in self.parameter_set_random_outcomes.all()],
        }

