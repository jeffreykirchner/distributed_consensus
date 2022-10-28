'''
gloabal functions related to parameter sets
'''

from django.db import models
from django.utils.translation import gettext_lazy as _

import main

class ChatTypes(models.TextChoices):
    '''
    chat types
    '''
    ALL = 'All', _('All')
    INDIVIDUAL = 'Individual', _('Individual')

class ExperimentPhase(models.TextChoices):
    '''
    experiment phases
    '''
    INSTRUCTIONS = 'Instructions', _('Instructions')
    RUN = 'Run', _('Run')
    PAY = 'Pay', _('Pay')
    RESULTS = 'Results', _('Results')
    DONE = 'Done', _('Done')

class PartModes(models.TextChoices):
    '''
    part modes
    '''
    A = 'A', _('A')
    B = 'B', _('B')
    C = 'C', _('C')

