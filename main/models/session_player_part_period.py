'''
session player period results
'''

import logging

from django.db import models

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

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID:{self.session_player_part.session_player}, Part:{self.session_player_part}, Period:{self.parameter_set_labels_period.period_number}"

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

        if random_outcome_counts_sorted[0]['sum'] >= self.session_part_period.session_part.parameter_set_part.minimum_for_majority:
            self.majority_choice = random_outcome_counts_sorted[0]['random_outcome']
            self.save()

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

        group_choices = [i.json_for_group() if i.choice else None for i in self.get_group_members()]

        return{
            "id" : self.id,    
            #"earnings" : self.earnings,
            "parameter_set_labels_period" : self.parameter_set_labels_period.json(),
            "parameter_set_part_period" : self.session_part_period.parameter_set_part_period.json(),
            "choice" : self.choice.json() if self.choice else None,      

            "current_outcome_index" : -1,
            "current_outcome_id" : -1,   

            "majority_choice" : self.majority_choice.json_for_subject() if self.majority_choice else None,
            "group_choices" : group_choices,
        }
    
    def json_for_group(self):
        '''
        json object of model
        '''

        return {
            "id" : self.id,  
            "session_player_id" : self.session_player_part.session_player.id,
            "id_label" : self.session_player_part.session_player.parameter_set_player.id_label,
            "parameter_set_labels_period" : self.parameter_set_labels_period.json(),
            "choice" : self.choice.json() if self.choice else None, 
        }
         