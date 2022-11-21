'''
session player period results
'''

import logging

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from main.models import SessionPlayerPart
from main.models import ParameterSetLabelsPeriod
from main.models import ParameterSetRandomOutcome
from main.models import SessionPartPeriod

import main

class SessionPlayerPartPeriod(models.Model):
    '''
    session player part period model
    '''
    session_player_part = models.ForeignKey(SessionPlayerPart, on_delete=models.CASCADE, related_name="session_player_part_periods_a")
    parameter_set_labels_period = models.ForeignKey(ParameterSetLabelsPeriod, on_delete=models.CASCADE, related_name="session_player_part_periods_b", blank=True, null=True)
    choice =  models.ForeignKey(ParameterSetRandomOutcome, on_delete=models.CASCADE, related_name="session_player_part_periods_c", blank=True, null=True)
    session_part_period = models.ForeignKey(SessionPartPeriod, on_delete=models.CASCADE, related_name="session_player_part_periods_d", blank=True, null=True)
    majority_choice = models.ForeignKey(ParameterSetRandomOutcome, on_delete=models.CASCADE, related_name="session_player_part_periods_e", null=True, blank=True)

    #earnings = models.IntegerField(verbose_name='Period Earnings', default=0)        #earnings in cents this period
    choice_length = models.IntegerField(verbose_name='Choice Length', default=0)      #time in ms it took subjects to make choice 
    json_for_group_json = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)
    indexes_json = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID: {self.id}, ID_label:{self.session_player_part.session_player}, Part:{self.session_player_part}, Period:{self.parameter_set_labels_period.period_number}"

    class Meta:
        
        verbose_name = 'Session Player Part Period'
        verbose_name_plural = 'Session Player Part Periods'
        ordering = ['session_player_part__session_player', 'parameter_set_labels_period__period_number']
        constraints = [
            models.UniqueConstraint(fields=['session_player_part', 'parameter_set_labels_period'], name='unique_session_player_period_part'),
        ]

    def get_group_labels(self):
        '''
        return list of labels for group
        '''        
        return [i.json_for_group() for i in self.get_group_members()]
    
    def get_group_number(self):
        '''
        return group number
        '''
        return self.session_player_part.parameter_set_player_part.group
    
    def get_group_members(self):
        '''
        return a list of SessionPlayerPartPeriod who in are this group
        '''
        parameter_set_part_period = self.session_part_period.parameter_set_part_period

        return main.models.SessionPlayerPartPeriod.objects.filter(session_part_period__parameter_set_part_period=parameter_set_part_period) \
                                                          .filter(session_player_part__parameter_set_player_part__group=self.get_group_number())
    
    def get_part_period_indexes(self):
        '''
        return part and period indexes
        '''

        if not self.indexes_json:
            self.indexes_json = {"part_number" : self.session_part_period.session_part.parameter_set_part.part_number-1,
                                 "period_number" : self.session_part_period.parameter_set_part_period.period_number-1}
            self.save()

        return self.indexes_json

    def calc_majority_choice(self):
        '''
        calc majority choice for this period
        '''
        logger = logging.getLogger(__name__)

        random_outcomes = self.parameter_set_labels_period.parameter_set_labels.parameter_set.parameter_set_random_outcomes.all()
        random_outcome_counts = []

        for i in random_outcomes:

            v = {'random_outcome' : i,
                 'sum' : self.get_group_members().filter(choice=i).count()}

            random_outcome_counts.append(v)
        
        random_outcome_counts_sorted = sorted(random_outcome_counts, key=lambda d: d['sum'], reverse=True) 

        #logger.info(f'Player:{self.session_player_part.session_player.parameter_set_player.id_label}, random_outcome_counts_sorted: {random_outcome_counts_sorted}')

        indexes = self.get_part_period_indexes()
        part_number = indexes["part_number"]
        period_number = indexes["period_number"]
        session_player_part_period = self.session_player_part.session_player.session_player_parts_json[part_number]["session_player_part_periods"][period_number]

        #if player in majority store it                                                                     
        if random_outcome_counts_sorted[0]['sum'] >= self.session_part_period.session_part.parameter_set_part.minimum_for_majority:
            self.majority_choice = random_outcome_counts_sorted[0]['random_outcome']
            self.save()

            session_player_part_period["majority_choice"] = self.majority_choice.json()
        
        #convert outcome to json format
        for index, i in enumerate(random_outcome_counts):
            random_outcome_counts[index]["random_outcome"] = random_outcome_counts[index]["random_outcome"].json()

        #store totals
        session_player_part_period["random_outcomes"] = random_outcome_counts

        self.session_player_part.session_player.save()

    def write_summary_download_csv(self, writer):
        '''
        take csv writer and add row
        '''

        writer.writerow([self.session_period.session.id,
                         self.session_period.period_number,
                         self.session_player.player_number,
                         self.session_player.parameter_set_player.id_label,])
                         
        
    def json_for_subject(self):
        '''
        json object of model
        '''

        # group_choices = [i.json_for_group() for i in self.get_group_members()]
        
        parameter_set_json =  self.session_player_part.session_player.session.parameter_set_json
        indexes = self.get_part_period_indexes()

        return{
            "id" : self.id,    
            #"earnings" : self.earnings,
            "parameter_set_labels_period" : self.parameter_set_labels_period.json(),
            #"parameter_set_part_period" : self.session_part_period.parameter_set_part_period.json(),
            "parameter_set_part_period" : parameter_set_json["parameter_set_parts"][indexes["part_number"]]
                                                            ["parameter_set_part_periods"][indexes["period_number"]],
            
            "choice" : self.choice.json() if self.choice else None,      
            "choice_length" : self.choice_length,

            "current_outcome_index" : -1,
            "current_outcome_id" : -1,   

            "majority_choice" : self.majority_choice.json_for_subject() if self.majority_choice else None,
            # "group_choices" : group_choices,

            "group_number" : self.get_group_number(),

            "paid" : self.session_part_period.paid,
        }
    
    def json_for_group(self, refresh_needed=False):
        '''
        json object of model
        '''

        if not self.json_for_group_json:
            
            self.json_for_group_json = {
                #"id" : self.id,  
                "session_player_id" : self.session_player_part.session_player.id,
                "id_label" : self.session_player_part.session_player.parameter_set_player.id_label,
                "parameter_set_labels_period" : self.parameter_set_labels_period.json_for_subject(),
                #"choice" : self.choice.json_for_subject() if self.choice else None, 
            }

            self.save()
        
        if refresh_needed:
            self.json_for_group_json["choice"] = self.choice.json_for_subject()
            self.save()

        return self.json_for_group_json
         