'''
parameterset parts edit form
'''

from django import forms

from main.globals import PartModes

from main.models import ParameterSetPart

class ParameterSetPartForm(forms.ModelForm):
    '''
    parameterset part edit form
    '''

    mode = forms.ChoiceField(label="Choice Mode",
                             choices=PartModes.choices,
                             widget=forms.Select(attrs={"v-model":"current_parameter_set_part.mode",}))

    minimum_for_majority = forms.IntegerField(label='Minimum for Majority',
                                              min_value=1,
                                              widget=forms.NumberInput(attrs={"min":"1",
                                                                              "v-model":"current_parameter_set_part.minimum_for_majority"}))

    pay_choice_majority = forms.DecimalField(label='Pay if choice in majority',
                                                    min_value=0,
                                                    widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_part.pay_choice_majority",
                                                                                    "min":"0",
                                                                                    "step":"0.01"}))

    pay_choice_minority = forms.DecimalField(label='Pay if choice in minority',
                                                    min_value=0,
                                                    widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_part.pay_choice_minority",
                                                                                    "min":"0",
                                                                                    "step":"0.01"}))

    pay_label_majority = forms.DecimalField(label='Pay if label in majority',
                                                    min_value=0,
                                                    widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_part.pay_label_majority",
                                                                                    "min":"0",
                                                                                    "step":"0.01"}))

    pay_label_minority = forms.DecimalField(label='Pay if label in minority',
                                                    min_value=0,
                                                    widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_part.pay_label_minority",
                                                                                    "min":"0",
                                                                                    "step":"0.01"}))


    class Meta:
        model=ParameterSetPart
        fields =['mode', 'minimum_for_majority', 'pay_choice_majority', 'pay_choice_minority', 'pay_label_majority', 'pay_label_minority']
    
