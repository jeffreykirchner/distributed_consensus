'''
parameter set
'''
import logging

from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError

from main.globals import PartModes

from main.models import ParameterSet
from main.models import InstructionSet

import main

class ParameterSetPart(models.Model):
    '''
    parameter set part
    '''    
    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_parts")
    instruction_set = models.ForeignKey(InstructionSet, on_delete=models.CASCADE, related_name="parameter_set_parts_b")

    mode = models.CharField(max_length=100, choices=PartModes.choices, default=PartModes.A)
    part_number = models.IntegerField(verbose_name='Part Number', default=0)
    minimum_for_majority = models.IntegerField(verbose_name='Minimum for Majority', default=7)                #minimum required for a majority

    pay_choice_majority = models.DecimalField(verbose_name = 'Pay if choice in majority choice', decimal_places=2, default=0, max_digits=4)     #payments based on choices and labels
    pay_choice_minority = models.DecimalField(verbose_name = 'Pay if choice in minority choice', decimal_places=2, default=0, max_digits=4)

    pay_label_majority = models.DecimalField(verbose_name = 'Pay if label in majority choice', decimal_places=2, default=0, max_digits=4)
    pay_label_minority = models.DecimalField(verbose_name = 'Pay if label in minority choice', decimal_places=2, default=0, max_digits=4)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Part {self.part_number}'

    class Meta:
        verbose_name = 'Parameter Set Part'
        verbose_name_plural = 'Parameter Set Parts'
        ordering=['part_number']
    
    def from_dict(self, new_ps):
        '''
        load values from dict
        '''
        logger = logging.getLogger(__name__) 

        message = "Parameters loaded successfully."
        status = "success"

        try:
            self.mode = new_ps.get("mode")
            self.part_number = new_ps.get("part_number")
            self.minimum_for_majority = new_ps.get("minimum_for_majority")
            self.pay_choice_majority = new_ps.get("pay_choice_majority")
            self.pay_choice_minority = new_ps.get("pay_choice_minority")
            self.pay_label_majority = new_ps.get("pay_label_majority")
            self.pay_label_minority = new_ps.get("pay_label_minority")
            self.instruction_set = InstructionSet.objects.get(label=new_ps.get("instruction_set")["label"])

            #parameter_set_part_periods
            new_parameter_set_part_periods = new_ps.get("parameter_set_part_periods")
            for index, p in enumerate(self.parameter_set_part_periods_a.all()):                
                p.from_dict(new_parameter_set_part_periods[index])
            
            self.save()
        except IntegrityError as exp:
            message = f"Failed to load parameter set part: {exp}"
            status = "fail"
            logger.warning(message)

        return {"status" : status, "message" :  message}

    def setup(self):
        '''
        default setup
        '''    
        pass
    
    def setup_periods(self):
        '''
        update the number player parts
        '''

        difference = self.parameter_set_part_periods_a.all().count() - self.parameter_set.period_count

        if difference>0:
            for i in range(difference):
                self.parameter_set_part_periods_a.last().delete()            
        elif difference<0:
            for i in range(abs(difference)):
                main.models.ParameterSetPartPeriod.objects.create(parameter_set_part=self)
        
        for index, i in enumerate(self.parameter_set_part_periods_a.all()):
            i.period_number = index + 1
            i.save()
        
    def randomize(self):
        '''
        randomize part
        '''

        for i in self.parameter_set_part_periods_a.all():
            i.randomize()

    def json(self):
        '''
        return json object of model
        '''
        return{
            "id" : self.id,
            "mode" : self.mode,
            "part_number" : self.part_number,
            "minimum_for_majority" : self.minimum_for_majority,
            "parameter_set_part_periods" : [p.json() for p in self.parameter_set_part_periods_a.all()],
            "pay_choice_majority" : self.pay_choice_majority,
            "pay_choice_minority" : self.pay_choice_minority,
            "pay_label_majority" : self.pay_label_majority,
            "pay_label_minority" : self.pay_label_minority,
            "instruction_set" : self.instruction_set.json_min(),
        }
    
    def json_for_subject(self):
        '''
        return json object for subject
        '''
        return{
            "id" : self.id,
            "mode" : self.mode,
            "part_number" : self.part_number,
            "minimum_for_majority" : self.minimum_for_majority,
            "pay_choice_majority" : str(self.pay_choice_majority),
            "pay_choice_minority" : str(self.pay_choice_minority),
            "pay_label_majority" : str(self.pay_label_majority),
            "pay_label_minority" : str(self.pay_label_minority),
            "instruction_set" : self.instruction_set.json_min(),
        }

