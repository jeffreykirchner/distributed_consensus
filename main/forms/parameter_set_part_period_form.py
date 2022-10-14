'''
parameterset parts edit form
'''

from django import forms

from main.globals import PartModes

from main.models import ParameterSetPartPeriod

import main

class ParameterSetPartPeriodForm(forms.ModelForm):
    '''
    parameterset part period edit form
    '''

    parameter_set_random_outcome = forms.ModelChoiceField(label='Label',          
                                   empty_label=None,                          
                                   queryset=main.models.ParameterSetRandomOutcome.objects.none(),
                                   widget=forms.Select(attrs={"v-model":"current_parameter_set_part_period.parameter_set_random_outcome.id"}))


    class Meta:
        model=ParameterSetPartPeriod
        fields =['parameter_set_random_outcome']
    
