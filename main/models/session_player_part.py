'''
session player part 
'''

#import logging

from django.db import models

from main.models import SessionPlayer
from main.models import SessionPart
from main.models import ParameterSetPlayerPart

import main

class SessionPlayerPart(models.Model):
    '''
    session player part model
    '''
    session_part = models.ForeignKey(SessionPart, on_delete=models.CASCADE, related_name="session_player_parts_a")
    session_player = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_parts_b")
    parameter_set_player_part = models.ForeignKey(ParameterSetPlayerPart, on_delete=models.CASCADE, related_name="session_player_parts_c", null=True, blank=True)

    earnings = models.IntegerField(verbose_name='Part Earnings', default=0)        #earnings in cents this period
    results_complete = models.BooleanField(default=False, verbose_name="Results Complete")

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Player {self.session_player.parameter_set_player.id_label}, Part {self.session_part.parameter_set_part.part_number}"

    class Meta:
        
        verbose_name = 'Session Player Part'
        verbose_name_plural = 'Session Player Part'
        ordering = ['session_player', 'session_part']
        constraints = [
            models.UniqueConstraint(fields=['session_player', 'session_part'], name='unique_session_player_period'),
        ]
    
    def setup(self):
        '''
        setup player part
        '''

        session_player_part_periods = []

        for i in range(self.parameter_set_player_part.parameter_set_player.parameter_set.period_count):
            parameter_set_labels_period = self.parameter_set_player_part \
                                              .parameter_set_labels \
                                              .parameter_set_labels_period_a \
                                              .get(period_number=i+1)  
            
            session_part_period = self.session_part.session_part_periods_a.get(parameter_set_part_period__period_number=i+1)

            session_player_part_periods.append(main.models.SessionPlayerPartPeriod(session_player_part=self, \
                                                                                   parameter_set_labels_period=parameter_set_labels_period,
                                                                                   session_part_period=session_part_period))
        
        main.models.SessionPlayerPartPeriod.objects.bulk_create(session_player_part_periods)

    def write_summary_download_csv(self, writer):
        '''
        take csv writer and add row
        '''


        writer.writerow([self.session_period.session.id,
                         self.session_period.period_number,
                         self.session_player.player_number,
                         self.session_player.parameter_set_player.id_label,
                         self.earnings,])
    
    def get_current_session_player_part_period(self):
        '''
        return the current session player part period
        '''
        return self.session_player_part_periods_a.get(session_part_period=self.session_part.current_session_part_period)
        
    def json_for_subject(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,    
            "earnings" : self.earnings,
            "session_player_part_periods" : [i.json_for_subject() for i in self.session_player_part_periods_a.all()],
            "results_complete" : self.results_complete,
            #"parameter_set_player_part" : self.parameter_set_player_part.json(),
        }