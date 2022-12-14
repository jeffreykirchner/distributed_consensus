'''
build forms
'''

from .login_form import LoginForm
from .parameters_form import ParametersForm
from .session_form import SessionForm
from .session_send_invitation_form import  SessionInvitationForm
from .import_parameters_form import ImportParametersForm

from .parameter_set_form import ParameterSetForm
from .parameter_set_part_form import ParameterSetPartForm
from .parameter_set_part_period_form import ParameterSetPartPeriodForm
from .parameter_set_player_form import ParameterSetPlayerForm
from .parameter_set_player_part_form import ParameterSetPlayerPartForm
from .parameter_set_labels_form import ParameterSetLabelsForm
from .parameter_set_labels_period_form import ParameterSetLabelsPeriodForm
from .parameter_set_random_outcome_form import ParameterSetRandomOutcomeForm

from .session_player_name_etc_form import StaffEditNameEtcForm

from .session_form_admin import SessionFormAdmin
from .instruction_set_form_admin import InstructionSetFormAdmin
from .instruction_form_admin import InstructionFormAdmin

from .end_game_form import EndGameForm
