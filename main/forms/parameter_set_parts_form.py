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

    class Meta:
        model=ParameterSetPart
        fields =['mode']
    
