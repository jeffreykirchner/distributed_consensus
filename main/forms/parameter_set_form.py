'''
Parameterset edit form
'''

from django import forms

from main.models import ParameterSet

import  main

class ParameterSetForm(forms.ModelForm):
    '''
    Parameterset edit form
    '''
    part_count = forms.IntegerField(label='Number of Parts',
                                      min_value=1,
                                      widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.part_count",
                                                                      "step":"1",
                                                                      "min":"1"}))

    period_count = forms.IntegerField(label='Periods per Part',
                                      min_value=1,
                                      widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.period_count",
                                                                      "step":"1",
                                                                      "min":"1"}))

    period_length = forms.IntegerField(label='Period Length (seconds)',
                                       min_value=1,
                                       widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.period_length",
                                                                       "step":"1",
                                                                       "min":"1"}))

    label_set_count = forms.IntegerField(label='Label Set Count',
                                      min_value=1,
                                      widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.label_set_count",
                                                                      "step":"1",
                                                                      "min":"1"}))

    show_instructions = forms.ChoiceField(label='Show Instructions',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.show_instructions",}))

    test_mode = forms.ChoiceField(label='Test Mode',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.test_mode",}))

    class Meta:
        model=ParameterSet
        fields =['part_count', 'period_count', 'period_length', 'label_set_count', 'show_instructions', 'test_mode',]
                 
