'''
build test
'''
import imp
import logging
import sys

from django.test import TestCase


from main.models import Session

from main.consumers import take_choice

import main

class TestSubjectConsumer(TestCase):
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
    
    def test_choice(self):
        '''
        test choices
        '''

        self.session_small.start_experiment()
        session_player = self.session_small.session_players_a.all()[1]

        #part 1 period 1       
        session_player_part_period = session_player.get_current_session_player_part().get_current_session_player_part_period()

        data ={'data':{'random_outcome_id': self.session_small.parameter_set.parameter_set_random_outcomes.all()[1].id, 
                            'part_period_id': session_player_part_period.id, 
                            'current_index': {'part_index': 0, 'period_index': 0}}}
                
        r = take_choice(self.session_small.id, session_player.id, data)
        self.assertEqual(r["value"], "success")
        session_player_part_period = session_player.get_current_session_player_part().get_current_session_player_part_period()
        self.assertEqual(session_player_part_period.choice, self.session_small.parameter_set.parameter_set_random_outcomes.all()[1])
        self.assertEqual(session_player_part_period.session_player_part.session_part.parameter_set_part.part_number, 1)

        #part 2 period 1
        self.session_small = Session.objects.get(title='Test Small')
        self.session_small.current_session_part = self.session_small.session_parts_a.all()[1]
        self.session_small.save()

        session_player = self.session_small.session_players_a.all()[1]

        session_player_part_period = session_player.get_current_session_player_part().get_current_session_player_part_period()

        data ={'data':{'random_outcome_id': self.session_small.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                       'part_period_id': session_player_part_period.id, 
                       'current_index': {'part_index': 1, 'period_index': 0}}}
                
        r = take_choice(self.session_small.id, session_player.id, data)
        self.assertEqual(r["value"], "success")
        session_player_part_period = session_player.get_current_session_player_part().get_current_session_player_part_period()
        self.assertEqual(session_player_part_period.choice, self.session_small.parameter_set.parameter_set_random_outcomes.all()[0])
        self.assertEqual(session_player_part_period.session_player_part.session_part.parameter_set_part.part_number, 2)
        
