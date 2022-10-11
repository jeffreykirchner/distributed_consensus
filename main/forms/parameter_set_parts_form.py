'''
parameterset parts edit form
'''

from django import forms

from main.globals import PartModes

from main.models import ParameterSetPart

class ParameterSetPartsForm(forms.ModelForm):
    '''
    parameterset player edit form
    '''

    mode = forms.ChoiceField(label="Choice Mode",
                             choices=PartModes.choices,
                             widget=forms.Select(attrs={"v-model":"current_parameter_set_part.mode",}))

    minimum_for_majority = forms.IntegerField(label='Minimum for Majority',
                                              min_value=1,
                                              widget=forms.NumberInput(attrs={"min":"1",
                                                                              "v-model":"current_parameter_set_part.minimum_for_majority"}))

    class Meta:
        model=ParameterSetPart
        fields =['mode', 'minimum_for_majority']
    
