'''
session player period results
'''

#import logging

from django.db import models

from main.models import SessionPlayerPart
from main.models import ParameterSetLabelsPeriod
from main.models import ParameterSetRandomOutcome
from main.models import SessionPartPeriod

class SessionPlayerPartPeriod(models.Model):
    '''
    session player part period model
    '''
    session_player_part = models.ForeignKey(SessionPlayerPart, on_delete=models.CASCADE, related_name="session_player_part_periods_a")
    parameter_set_labels_period = models.ForeignKey(ParameterSetLabelsPeriod, on_delete=models.CASCADE, related_name="session_player_part_periods_b", blank=True, null=True)
    choice =  models.ForeignKey(ParameterSetRandomOutcome, on_delete=models.CASCADE, related_name="session_player_part_periods_c", blank=True, null=True)
    session_part_period = models.ForeignKey(SessionPartPeriod, on_delete=models.CASCADE, related_name="session_player_part_periods_d", blank=True, null=True)

    earnings = models.IntegerField(verbose_name='Period Earnings', default=0)        #earnings in cents this period

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID: {self.session_player_part.session_player} \
                 , Period {self.parameter_set_labels_period.period_number}"

    class Meta:
        
        verbose_name = 'Session Player Part Period'
        verbose_name_plural = 'Session Player Part Periods'
        ordering = ['session_player_part', 'parameter_set_labels_period']
        constraints = [
            models.UniqueConstraint(fields=['session_player_part', 'parameter_set_labels_period'], name='unique_session_player_period_part'),
        ]
    
    def write_summary_download_csv(self, writer):
        '''
        take csv writer and add row
        '''


        writer.writerow([self.session_period.session.id,
                         self.session_period.period_number,
                         self.session_player.player_number,
                         self.session_player.parameter_set_player.id_label,
                         self.earnings,])
        
    def json_for_subject(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,    
            "earnings" : self.earnings,
            "parameter_set_labels_period" : self.parameter_set_labels_period.json(),
            "choice" : self.choice.json() if self.choice else None,      

            "current_outcome_index" : -1,
            "current_outcome_id" : -1,     
        }