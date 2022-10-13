'''
parameterset player part edit form
'''

from django import forms

from main.models import ParameterSetPlayerPart

import main

class ParameterSetPlayerPartForm(forms.ModelForm):
    '''
    parameterset player part edit form
    '''

    parameter_set_labels = forms.ModelChoiceField(label='Label Set',                                    
                                                  queryset=main.models.ParameterSetLabels.objects.all(),
                                                  widget=forms.Select(attrs={"v-model":"current_parameter_set_player_part.parameter_set_labels.id"}))
 
    group = forms.IntegerField(label='Group',
                               min_value=0,
                               widget=forms.NumberInput(attrs={"min":"1",
                                                               "v-model":"current_parameter_set_player_part.group"}))

    class Meta:
        model=ParameterSetPlayerPart
        fields =['parameter_set_labels', 'group']
    
