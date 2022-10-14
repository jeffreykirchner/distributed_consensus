'''
parameterset labels period edit form
'''

from django import forms

from main.globals import PartModes

from main.models import ParameterSetLabelsPeriod

import main

class ParameterSetLabelsPeriodForm(forms.ModelForm):
    '''
    parameterset player labels period form
    '''

    label = forms.ModelChoiceField(label='Label',              
                                   empty_label=None,                       
                                   queryset=main.models.ParameterSetRandomOutcome.objects.none(),
                                   widget=forms.Select(attrs={"v-model":"current_parameter_set_labels_period.label.id"}))

    class Meta:
        model=ParameterSetLabelsPeriod
        fields =['label']
    
