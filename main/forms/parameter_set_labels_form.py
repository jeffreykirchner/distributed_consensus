'''
parameterset labels edit form
'''

from django import forms

from main.models import ParameterSetLabels

class ParameterSetLabelsForm(forms.ModelForm):
    '''
    parameterset player edit form
    '''

    name =  forms.CharField(label='Name',
                            widget=forms.TextInput(attrs={"v-model":"current_parameter_set_label.name",}))

    class Meta:
        model=ParameterSetLabels
        fields =['name']
    
