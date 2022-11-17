'''
parameterset randome outcome edit form
'''

from django import forms
from django.db.models.query import RawQuerySet

from main.models import ParameterSetRandomOutcome

class ParameterSetRandomOutcomeForm(forms.ModelForm):
    '''
    parameterset random outcome edit form
    '''

    name = forms.CharField(label='Name',
                           widget=forms.TextInput(attrs={"v-model":"current_random_outcome.name",}))
    
    abbreviation = forms.CharField(label='Abbreviation',
                                   widget=forms.TextInput(attrs={"v-model":"current_random_outcome.abbreviation",}))
    
    image = forms.CharField(label='Image File',
                            widget=forms.TextInput(attrs={"v-model":"current_random_outcome.image",}))
    
    label = forms.CharField(label='Label File',
                            widget=forms.TextInput(attrs={"v-model":"current_random_outcome.label",}))

    class Meta:
        model=ParameterSetRandomOutcome
        fields =['name', 'abbreviation', 'image', 'label']
    
