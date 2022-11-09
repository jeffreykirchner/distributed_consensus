'''
build test
'''
from decimal import Decimal
import imp
import logging
from operator import truediv
import sys

from django.test import TestCase

from main.models import Session

from main.consumers import take_chat
from main.consumers import take_next_phase
from main.consumers import take_choice
from main.consumers import take_ready_to_go_on
from main.consumers import take_payment_periods
from main.consumers import take_next_phase
from main.consumers import take_check_all_choices_in

from main.globals import ExperimentPhase

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
    
    def test_majority_1(self):
        '''
        test no majority calculation
        '''
        logger = logging.getLogger(__name__)

        self.session_large.start_experiment()

        #check no majority
        for j in range(self.session_large.parameter_set.period_count):

            for index, i in enumerate(self.session_large.session_players_a.all()):
                session_player_part_period = i.get_current_session_player_part().get_current_session_player_part_period()      

                if index<self.session_large.session_players_a.all().count()/2:       
                    data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                           'part_period_id': session_player_part_period.id, 
                           'current_index': {'part_index': 0, 'period_index': j}}}
                else:
                    data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[1].id, 
                            'part_period_id': session_player_part_period.id, 
                            'current_index': {'part_index': 0, 'period_index': j}}}
                
                r = take_choice(self.session_large.id, i.id, data)   
                self.assertEqual(r["value"], "success")
     
            self.assertNotEqual(self.session_large.check_advance_period(), None)
        
        self.session_large.current_session_part.calc_results()

        self.assertEqual(self.session_large.current_session_part.parameter_set_part.part_number, 1)

        v = self.session_large.session_players_a.all()[0].session_player_parts_b.all()[0].session_player_part_periods_a.all()[0]
        self.assertEqual(None, v.majority_choice)

    def test_majority_2(self):
        '''
        test majority calculation
        '''
        logger = logging.getLogger(__name__)
        
        self.session_large.start_experiment()

        #check minimum majority        
        for j in range(self.session_large.parameter_set.period_count):

            for index, i in enumerate(self.session_large.session_players_a.all()):
                session_player_part_period = i.get_current_session_player_part().get_current_session_player_part_period()      

                minimum_for_majority = session_player_part_period.session_player_part.session_part.parameter_set_part.minimum_for_majority

                #logger.info(f'Session player part period: Player:{i.parameter_set_player.id_label} Period:{session_player_part_period.parameter_set_labels_period.period_number}')

                if index < minimum_for_majority:    
                    data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                           'part_period_id': session_player_part_period.id, 
                           'current_index': {'part_index': 0, 'period_index': j}}}
                    
                else:
                    data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[1].id, 
                            'part_period_id': session_player_part_period.id, 
                            'current_index': {'part_index': 0, 'period_index': j}}}

                r = take_choice(self.session_large.id, i.id, data)   
                self.assertEqual(r["value"], "success")

                #session_player_part_period.save()   
                #logger.info(f'Period: {j}, Player:{index}, Choice:{session_player_part_period.choice}')         
                          
            self.assertNotEqual(self.session_large.check_advance_period(), None)
        
        #logger.info(f"Current Session Part: {self.session_large.current_session_part.parameter_set_part.part_number}")
        self.assertEqual(self.session_large.current_session_part.parameter_set_part.part_number, 1)

        v = self.session_large.session_players_a.all()[0].session_player_parts_b.all()[0].session_player_part_periods_a.all()[0]
        self.assertEqual(self.session_large.parameter_set.parameter_set_random_outcomes.all()[0], v.majority_choice)
        self.assertEqual(self.session_large.parameter_set.parameter_set_random_outcomes.all()[0], v.choice)

        v = self.session_large.session_players_a.all()[11].session_player_parts_b.all()[0].session_player_part_periods_a.all()[0]
        self.assertEqual(self.session_large.parameter_set.parameter_set_random_outcomes.all()[1], v.choice)

        #check advance second part
        #press ready to go on
        for index, i in enumerate(self.session_large.session_players_a.all()):
            session_player_part = i.get_current_session_player_part()
            session_player_part_period = session_player_part.get_current_session_player_part_period()
            data = {'data': {'player_part_id': session_player_part.id, 
                             'current_index': {'part_index': 0, 
                                               'period_index': session_player_part_period.parameter_set_labels_period.period_number-1}}}

            r = take_ready_to_go_on(self.session_large.id, i.id, data)   
            self.assertEqual(r["value"], "success")

        self.assertNotEqual(self.session_large.check_advance_period(), None)
        self.assertEqual(self.session_large.current_session_part.parameter_set_part.part_number, 2)

        #check minimum majority        
        group_1_players = self.session_large.session_players_a.all()[0].session_player_parts_b.all()[1].session_player_part_periods_a.all()[0].get_group_members()

        for j in range(self.session_large.parameter_set.period_count):

            for index, i in enumerate(self.session_large.session_players_a.all()):
                session_player_part_period = i.get_current_session_player_part().get_current_session_player_part_period()      

                if session_player_part_period in group_1_players:
                    minimum_for_majority = session_player_part_period.session_player_part.session_part.parameter_set_part.minimum_for_majority

                    if index < minimum_for_majority:      
                        data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                           'part_period_id': session_player_part_period.id, 
                           'current_index': {'part_index': 0, 'period_index': j}}}
                    else:
                        data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[1].id, 
                           'part_period_id': session_player_part_period.id, 
                           'current_index': {'part_index': 0, 'period_index': j}}}

                    r = take_choice(self.session_large.id, i.id, data)   
                    self.assertEqual(r["value"], "success")
                else:
                    data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                           'part_period_id': session_player_part_period.id, 
                           'current_index': {'part_index': 0, 'period_index': j}}}

                    r = take_choice(self.session_large.id, i.id, data)   
                    self.assertEqual(r["value"], "success")
                           
            self.assertNotEqual(self.session_large.check_advance_period(), None)  
            
        
        self.assertEqual(self.session_large.current_session_part.parameter_set_part.part_number, 3)

        #advance to part 3
        for j in range(self.session_large.parameter_set.period_count):

            for index, i in enumerate(self.session_large.session_players_a.all()):
                session_player_part_period = i.get_current_session_player_part().get_current_session_player_part_period()      
  
                data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                        'part_period_id': session_player_part_period.id, 
                        'current_index': {'part_index': 0, 'period_index': j}}}

                r = take_choice(self.session_large.id, i.id, data)   
                self.assertEqual(r["value"], "success")
                           
            self.assertNotEqual(self.session_large.check_advance_period(), None)

        self.assertEqual(self.session_large.current_experiment_phase, ExperimentPhase.PAY)

        session_parts = self.session_large.session_parts_a.all()

        data = {'payment_periods': [{'id': session_parts[1].id, 'periods': '1'}, 
                                    {'id': session_parts[2].id, 'periods': '2'}]}
        r = take_payment_periods(self.session_large.id, data)
        self.assertEqual(r["value"], "success")

        self.session_large = Session.objects.get(title='Test Large')
        self.assertEqual(self.session_large.current_experiment_phase, ExperimentPhase.RESULTS)

        #check part 2

        v = self.session_large.session_players_a.all()[0].session_player_parts_b.all()[1].session_player_part_periods_a.all()[0]
        self.assertEqual(self.session_large.parameter_set.parameter_set_random_outcomes.all()[0], v.majority_choice)
        self.assertNotEqual(group_1_players[2].choice, v.majority_choice)

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

                data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                       'part_period_id': session_player_part_period.id, 
                       'current_index': {'part_index': 0, 'period_index': j}}}
                
                r = take_choice(self.session_large.id, i.id, data)   
                self.assertEqual(r["value"], "success")
            
            if j<19:
                self.assertNotEqual(self.session_large.check_advance_period(), None)

        self.assertEqual(self.session_large.current_session_part.parameter_set_part.part_number, 1)

        p1 = self.session_large.session_players_a.all()[0].get_current_session_player_part().get_current_session_player_part_period()
        p1.choice = self.session_large.parameter_set.parameter_set_random_outcomes.all()[1]
        p1.save()

        self.assertNotEqual(self.session_large.check_advance_period(), None)
        self.assertEqual(self.session_large.current_session_part.parameter_set_part.part_number, 1)

        #check player 1 in minority
        p1 = self.session_large.session_players_a.all()[0]
        self.assertEqual(Decimal('1'), p1.session_player_parts_b.first().earnings)

        #check player 2 in majority
        p2 = self.session_large.session_players_a.all()[1]
        self.assertEqual(Decimal('10'), p2.session_player_parts_b.first().earnings)

    def test_mode_b(self):
        '''
        test mode B 
        '''
        logger = logging.getLogger(__name__)
        self.session_large.start_experiment()

        #check advance second part
        self.session_large.current_session_part = self.session_large.session_parts_a.all()[1]
        self.session_large.save()

        self.assertEqual("Part 2",self.session_large.current_session_part.__str__())

        #check majority calculations
        for j in range(self.session_large.parameter_set.period_count):

            for i in self.session_large.session_players_a.all():
                session_player_part_period = i.get_current_session_player_part().get_current_session_player_part_period()  

                data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                       'part_period_id': session_player_part_period.id, 
                       'current_index': {'part_index': 0, 'period_index': j}}}
                
                r = take_choice(self.session_large.id, i.id, data)   
                self.assertEqual(r["value"], "success")            
            
            if j<19:
                self.assertNotEqual(self.session_large.check_advance_period(), None)
       
        self.assertEqual(self.session_large.current_session_part.parameter_set_part.part_number, 2)

        v = self.session_large.current_session_part.session_part_periods_a.all()[1]
        v.paid = True
        v.save()

        self.session_large.current_session_part.calc_results()

        v = self.session_large.session_players_a.all()[0].session_player_parts_b.all()[1].session_player_part_periods_a.all()[0]
        self.assertEqual(self.session_large.parameter_set.parameter_set_random_outcomes.all()[0], v.majority_choice)
        self.assertEqual(Decimal('1'), v.session_player_part.earnings)

        v = self.session_large.session_players_a.all()[1].session_player_parts_b.all()[1].session_player_part_periods_a.all()[0]
        self.assertEqual(self.session_large.parameter_set.parameter_set_random_outcomes.all()[0], v.majority_choice)
        self.assertEqual(Decimal('10'), v.session_player_part.earnings)
    
    def test_mode_c(self):
        '''
        test mode c
        '''
        logger = logging.getLogger(__name__)
        self.session_large.start_experiment()

        #check advance second part
        self.session_large.current_session_part = self.session_large.session_parts_a.all()[2]
        self.session_large.save()

        self.assertEqual("Part 3",self.session_large.current_session_part.__str__())

        #check majority calculations
        for j in range(self.session_large.parameter_set.period_count):

            for i in self.session_large.session_players_a.all():
                session_player_part_period = i.get_current_session_player_part().get_current_session_player_part_period() 

                data ={'data':{'random_outcome_id': self.session_large.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                       'part_period_id': session_player_part_period.id, 
                       'current_index': {'part_index': 0, 'period_index': j}}}
                
                r = take_choice(self.session_large.id, i.id, data)   
                self.assertEqual(r["value"], "success")            
            
            if j<19:
                self.assertNotEqual(self.session_large.check_advance_period(), None)
       
        self.assertEqual(self.session_large.current_session_part.parameter_set_part.part_number, 3)

        v = self.session_large.current_session_part.session_part_periods_a.all()[1]
        v.paid = True
        v.save()

        v = self.session_large.session_players_a.all()[1].session_player_parts_b.all()[2].session_player_part_periods_a.all()[1]
        v.choice = self.session_large.parameter_set.parameter_set_random_outcomes.all()[1]
        v.save()

        self.session_large.current_session_part.calc_results()

        #label in minority, choice in majority
        v = self.session_large.session_players_a.all()[0].session_player_parts_b.all()[2].session_player_part_periods_a.all()[0]
        self.assertEqual(self.session_large.parameter_set.parameter_set_random_outcomes.all()[0], v.majority_choice)
        self.assertEqual("Part 3",v.session_player_part.parameter_set_player_part.__str__())
        self.assertEqual(Decimal('2'), v.session_player_part.earnings)

        #label in majority, choice in majority
        v = self.session_large.session_players_a.all()[4].session_player_parts_b.all()[2].session_player_part_periods_a.all()[0]
        self.assertEqual(self.session_large.parameter_set.parameter_set_random_outcomes.all()[0], v.majority_choice)
        self.assertEqual("Part 3",v.session_player_part.parameter_set_player_part.__str__())
        self.assertEqual(Decimal('10'), v.session_player_part.earnings)

        #label in minority, choice in minority
        v = self.session_large.session_players_a.all()[1].session_player_parts_b.all()[2].session_player_part_periods_a.all()[0]
        self.assertEqual(self.session_large.parameter_set.parameter_set_random_outcomes.all()[0], v.majority_choice)
        self.assertEqual("Part 3",v.session_player_part.parameter_set_player_part.__str__())
        self.assertEqual(Decimal('1'), v.session_player_part.earnings)
    
    def test_session_phases(self):
        '''
        test session phases
        '''

        #instructions at start
        self.session_small.start_experiment()
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.INSTRUCTIONS)
        self.assertEqual(self.session_small.current_session_part.parameter_set_part.part_number, 1)

        #instructions for part 1 done
        r = take_next_phase(self.session_small.id, {})
        self.assertEqual(r["value"], "success")
        self.session_small = Session.objects.get(title='Test Small')
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.RUN)
        self.assertEqual(self.session_small.current_session_part.parameter_set_part.part_number, 1)

        #part 1 choices
        for j in range(self.session_small.parameter_set.period_count):

            for index, i in enumerate(self.session_small.session_players_a.all()):
                session_player_part_period = i.get_current_session_player_part().get_current_session_player_part_period()      

                data ={'data':{'random_outcome_id': self.session_small.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                        'part_period_id': session_player_part_period.id, 
                        'current_index': {'part_index': 0, 'period_index': j}}}

                r = take_choice(self.session_small.id, i.id, data)   
                self.assertEqual(r["value"], "success")  
                          
            self.assertNotEqual(self.session_small.check_advance_period(), None)
        
        self.session_small = Session.objects.get(title='Test Small')
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.RUN)
        self.assertEqual(self.session_small.current_session_part.parameter_set_part.part_number, 1)

        #part 1 results
        for index, i in enumerate(self.session_small.session_players_a.all()):
            session_player_part = i.get_current_session_player_part()
            session_player_part_period = session_player_part.get_current_session_player_part_period()
            data = {'data': {'player_part_id': session_player_part.id, 
                             'current_index': {'part_index': 0, 
                                               'period_index': session_player_part_period.parameter_set_labels_period.period_number-1}}}

            r = take_ready_to_go_on(self.session_small.id, i.id, data)   
            self.assertEqual(r["value"], "success")

        #part 2 instructions
        v = take_check_all_choices_in(self.session_small.id, {})
        self.assertEqual(r["value"], "success")
        self.session_small = Session.objects.get(title='Test Small')
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.INSTRUCTIONS)
        self.assertEqual(self.session_small.current_session_part.parameter_set_part.part_number, 2)

        #part 2 choices
        r = take_next_phase(self.session_small.id, {})
        self.assertEqual(r["value"], "success")
        self.session_small = Session.objects.get(title='Test Small')
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.RUN)
        self.assertEqual(self.session_small.current_session_part.parameter_set_part.part_number, 2)

        #part 2 choices
        for j in range(self.session_small.parameter_set.period_count):

            for index, i in enumerate(self.session_small.session_players_a.all()):
                session_player_part_period = i.get_current_session_player_part().get_current_session_player_part_period()      

                data ={'data':{'random_outcome_id': self.session_small.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                        'part_period_id': session_player_part_period.id, 
                        'current_index': {'part_index': 0, 'period_index': j}}}

                r = take_choice(self.session_small.id, i.id, data)   
                self.assertEqual(r["value"], "success")  
                          
            self.assertNotEqual(self.session_small.check_advance_period(), None)
        
        #part 3 instructions
        self.session_small = Session.objects.get(title='Test Small')
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.INSTRUCTIONS)
        self.assertEqual(self.session_small.current_session_part.parameter_set_part.part_number, 3)

        #part 3 run
        r = take_next_phase(self.session_small.id, {})
        self.assertEqual(r["value"], "success")
        self.session_small = Session.objects.get(title='Test Small')
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.RUN)
        self.assertEqual(self.session_small.current_session_part.parameter_set_part.part_number, 3)

        #part 3 choices
        for j in range(self.session_small.parameter_set.period_count):

            for index, i in enumerate(self.session_small.session_players_a.all()):
                session_player_part_period = i.get_current_session_player_part().get_current_session_player_part_period()      

                data ={'data':{'random_outcome_id': self.session_small.parameter_set.parameter_set_random_outcomes.all()[0].id, 
                        'part_period_id': session_player_part_period.id, 
                        'current_index': {'part_index': 0, 'period_index': j}}}

                r = take_choice(self.session_small.id, i.id, data)   
                self.assertEqual(r["value"], "success")  
                          
            self.assertNotEqual(self.session_small.check_advance_period(), None)
        
        #payment
        self.session_small = Session.objects.get(title='Test Small')
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.PAY)
        self.assertEqual(self.session_small.current_session_part.parameter_set_part.part_number, 3)

        session_parts = self.session_small.session_parts_a.all()

        data = {'payment_periods': [{'id': session_parts[1].id, 'periods': '1'}, 
                                    {'id': session_parts[2].id, 'periods': '2'}]}
        r = take_payment_periods(self.session_small.id, data)
        self.assertEqual(r["value"], "success")

        self.session_small = Session.objects.get(title='Test Small')
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.RESULTS)

        r = take_next_phase(self.session_small.id, {})
        self.assertEqual(r["value"], "success")
        self.session_small = Session.objects.get(title='Test Small')
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.NAMES)

        r = take_next_phase(self.session_small.id, {})
        self.assertEqual(r["value"], "success")
        self.session_small = Session.objects.get(title='Test Small')
        self.assertEqual(self.session_small.current_experiment_phase, ExperimentPhase.DONE)
        self.assertTrue(self.session_small.finished)









    
