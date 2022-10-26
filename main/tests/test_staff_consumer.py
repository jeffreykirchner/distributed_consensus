'''
build test
'''
from decimal import Decimal
import imp
import logging
import sys

from django.test import TestCase


from main.models import Session

from main.consumers import take_chat
from main.consumers import take_next_phase

import main

class TestStaffConsumer(TestCase):
    fixtures = ['auth_user.json', 'main.json']

    user = None
    session_small = None
    session_large = None
    session_player_1 = None

    def setUp(self):
        sys._called_from_test = True
        logger = logging.getLogger(__name__)

        self.session_small = Session.objects.get(title='Test Small')
        self.session_large = Session.objects.get(title='Test Large')
    
    def test_mode_a(self):
        '''
        test mode A 
        '''

        logger = logging.getLogger(__name__)
        self.session_large.start_experiment()

        #check majority calculations
        for j in range(self.session_large.parameter_set.period_count):

            for i in self.session_large.session_players_a.all():
                session_player_part_period = i.get_current_session_player_part().get_current_session_player_part_period()                
                session_player_part_period.choice = self.session_large.parameter_set.parameter_set_random_outcomes.all()[0]
                session_player_part_period.save()            
            
            self.session_large.current_session_part.advance_period()

        p1 = self.session_large.session_players_a.all()[0].get_current_session_player_part().get_current_session_player_part_period()
        p1.choice = self.session_large.parameter_set.parameter_set_random_outcomes.all()[1]
        p1.save()

        self.session_large.current_session_part.calc_results()

        #check player 1 in minority
        p1 = self.session_large.session_players_a.all()[0]
        self.assertEqual(Decimal('1'), p1.session_player_parts_b.first().earnings)

        #check player 2 in majority
        p2 = self.session_large.session_players_a.all()[1]
        self.assertEqual(Decimal('10'), p2.session_player_parts_b.first().earnings)
        
        




    
