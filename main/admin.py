'''
admin interface
'''

from django.contrib import admin
from django.contrib import messages
from django.conf import settings
from django.urls import resolve

from main.forms import ParametersForm
from main.forms import SessionFormAdmin
from main.forms import InstructionFormAdmin
from main.forms import InstructionSetFormAdmin

from main.models import Parameters
from main.models import ParameterSet
from main.models import ParameterSetPlayer
from main.models import ParameterSetPlayerPart
from main.models import ParameterSetPart
from main.models import ParameterSetPartPeriod
from main.models import ParameterSetRandomOutcome
from main.models import ParameterSetLabels
from main.models import ParameterSetLabelsPeriod

from main.models import Session
from main.models import SessionPlayer
from main.models import SessionPlayerChat
from main.models import SessionPlayerPart
from main.models import SessionPlayerPartPeriod
from main.models import SessionPart
from main.models import SessionPartPeriod

from main.models import  HelpDocs

from main.models.instruction_set import InstructionSet
from main.models.instruction import Instruction

admin.site.site_header = settings.ADMIN_SITE_HEADER

@admin.register(Parameters)
class ParametersAdmin(admin.ModelAdmin):
    '''
    parameters model admin
    '''
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    form = ParametersForm

    actions = []

@admin.register(ParameterSetPlayerPart)
class ParameterSetPlayerPartAdmin(admin.ModelAdmin):
    
    readonly_fields=['parameter_set_player', 'parameter_set_part', 'parameter_set_labels']
    list_display = ['group']

class ParameterSetPlayerPartInline(admin.TabularInline):

      extra = 0  
      model = ParameterSetPlayerPart
      can_delete = False   
      show_change_link = True
      fields=['group']

@admin.register(ParameterSetPlayer)
class ParameterSetPlayerAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False

    readonly_fields=['parameter_set']
    list_display = ['id_label']

    inlines = [
        ParameterSetPlayerPartInline,
      ]

class ParameterSetPlayerInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False

    extra = 0  
    model = ParameterSetPlayer
    can_delete = True   
    show_change_link = True

@admin.register(ParameterSetPartPeriod)
class ParameterSetPartPeriodAdmin(admin.ModelAdmin):

    def render_change_form(self, request, context, *args, **kwargs):
         context['adminform'].form.fields['parameter_set_random_outcome'].queryset = kwargs['obj'].parameter_set_part.parameter_set.parameter_set_random_outcomes.all()

         return super(ParameterSetPartPeriodAdmin, self).render_change_form(request, context, *args, **kwargs)
    
    readonly_fields=['parameter_set_part', 'period_number']
    list_display = ['period_number', 'parameter_set_random_outcome']


class ParameterSetPartPeriodInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False
    
    def render_change_form(self, request, context, *args, **kwargs):
         context['adminform'].form.fields['parameter_set_random_outcome'].queryset = kwargs['obj'].parameter_set_part.parameter_set.parameter_set_random_outcomes.all()

         return super(ParameterSetPartPeriodAdmin, self).render_change_form(request, context, *args, **kwargs)
    
    def get_parent_object_from_request(self, request):

        resolved = resolve(request.path_info)

        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent = self.get_parent_object_from_request(request)

        if db_field.name == 'parameter_set_random_outcome':            
            kwargs['queryset'] = parent.parameter_set.parameter_set_random_outcomes.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    extra = 0  
    model = ParameterSetPartPeriod
    can_delete = False         
    show_change_link = True
    fields = ['parameter_set_random_outcome']
    
@admin.register(ParameterSetPart)
class ParameterSetPartAdmin(admin.ModelAdmin):
    
    readonly_fields=['parameter_set']
    list_display = ['mode', 'minimum_for_majority', 'pay_choice_majority', 'pay_choice_minority', 'pay_label_majority', 'pay_label_minority']

    inlines = [
        ParameterSetPartPeriodInline,
      ]

class ParameterSetPartInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False

    extra = 0  
    model = ParameterSetPart
    can_delete = False   
    show_change_link = True
    fields = ['mode', 'minimum_for_majority', 'pay_choice_majority', 'pay_choice_minority', 'pay_label_majority', 'pay_label_minority']

class ParameterSetLabelsPeriodInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False

    def get_parent_object_from_request(self, request):

        resolved = resolve(request.path_info)

        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent = self.get_parent_object_from_request(request)

        if db_field.name == 'label':            
            kwargs['queryset'] = parent.parameter_set.parameter_set_random_outcomes.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    extra = 0  
    model = ParameterSetLabelsPeriod
    can_delete = False   
    show_change_link = True
    fields = ['label']

@admin.register(ParameterSetLabels)
class ParameterSetLabelsAdmin(admin.ModelAdmin):
    
    readonly_fields=['parameter_set']
    list_display = ['name']

    inlines = [
        ParameterSetLabelsPeriodInline,
      ]

class ParameterSetLabelsInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False

    extra = 0  
    model = ParameterSetLabels
    can_delete = False   
    show_change_link = True
    fields = ['name']

@admin.register(ParameterSet)
class ParameterSetAdmin(admin.ModelAdmin):
    inlines = [
        ParameterSetPlayerInline,
        ParameterSetPartInline,
        ParameterSetLabelsInline,
      ]

    list_display = ['id', 'part_count', 'period_count', 'period_length']

admin.site.register(HelpDocs)

class SessionPlayerPartPeriodInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False

    def get_parent_object_from_request(self, request):

        resolved = resolve(request.path_info)

        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent = self.get_parent_object_from_request(request)

        if db_field.name == 'choice':            
            kwargs['queryset'] = parent.session_player.session.parameter_set.parameter_set_random_outcomes.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    extra = 0  
    model = SessionPlayerPartPeriod
    can_delete = False   
    show_change_link = True
    fields = ['choice']
    #readonly_fields = ('',)

@admin.register(SessionPlayerPart)
class SessionPlayerPartAdmin(admin.ModelAdmin):
    
    # def render_change_form(self, request, context, *args, **kwargs):
    #      context['adminform'].form.fields['parameter_set_player'].queryset = kwargs['obj'].parameter_set_player.parameter_set.parameter_set_players.all()

    #      return super(ParameterSetSessionPlayerAdmin, self).render_change_form(request, context, *args, **kwargs)

    readonly_fields=['session_part', 'session_player', 'parameter_set_player_part']
    list_display = ['session_part', 'session_player', 'parameter_set_player_part']
    fields = ['session_part', 'session_player', 'parameter_set_player_part', 'current_instruction', 'current_instruction_complete', 'instructions_finished', 'results_complete']
    inlines = [
        SessionPlayerPartPeriodInline,
      ]

class SessionPlayerPartInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False

    extra = 0  
    model = SessionPlayerPart
    can_delete = False   
    show_change_link = True
    fields = ['session_part', 'session_player', 'parameter_set_player_part', 'current_instruction', 'current_instruction_complete', 'instructions_finished', 'results_complete']
    readonly_fields = ('session_part','session_player','parameter_set_player_part')

@admin.register(SessionPlayer)
class SessionPlayerAdmin(admin.ModelAdmin):
    
    def render_change_form(self, request, context, *args, **kwargs):
         context['adminform'].form.fields['parameter_set_player'].queryset = kwargs['obj'].parameter_set_player.parameter_set.parameter_set_players.all()

         return super(SessionPlayerAdmin, self).render_change_form(request, context, *args, **kwargs)

    readonly_fields=['session','player_number','player_key']
    list_display = ['parameter_set_player', 'name', 'student_id', 'email',]
    fields = ['session','name', 'student_id', 'email', 'parameter_set_player','player_number','player_key', 'name_submitted']
    inlines = [
        SessionPlayerPartInline,
      ]

class SessionPlayerInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False
    
    @admin.display(description='Player ID')
    def get_parameter_set_player_id_label(self, obj):
        return obj.parameter_set_player.id_label

    extra = 0  
    model = SessionPlayer
    can_delete = False   
    show_change_link = True
    fields = ['name', 'student_id', 'email', 'name_submitted']
    readonly_fields = ('get_parameter_set_player_id_label',)

class SessionPartPeriodInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False

    extra = 0  
    model = SessionPartPeriod
    can_delete = False   
    show_change_link = True
    fields = ['session_part', 'parameter_set_part_period', 'paid']
    readonly_fields = ('session_part', 'parameter_set_part_period')

@admin.register(SessionPart)
class SessionPartAdmin(admin.ModelAdmin):
       
    readonly_fields=['session', 'parameter_set_part']
    list_display = ['session', 'parameter_set_part']
    fields = ['session', 'parameter_set_part', 'show_results']
    inlines = [
        SessionPartPeriodInline,
      ]

class SessionPartInline(admin.TabularInline):

    def has_add_permission(self, request, obj=None):
        return False

    extra = 0  
    model = SessionPart
    can_delete = False   
    show_change_link = True
    fields = ['parameter_set_part']
    readonly_fields = ('parameter_set_part',)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    
    readonly_fields=['parameter_set', 'current_session_part','session_key','channel_key']
    list_display = ['title', 'creator']
    fields = ['parameter_set', 'creator', 'collaborators', 'current_session_part', 'title','current_experiment_phase', 'started',
              'session_key','channel_key','finished','shared','locked',]

    inlines = [
      SessionPlayerInline,  
      SessionPartInline,
      ]

#instruction set page
class InstructionPageInline(admin.TabularInline):
      '''
      instruction page admin screen
      '''
      extra = 0  
      form = InstructionFormAdmin
      model = Instruction
      can_delete = True

@admin.register(InstructionSet)
class InstructionSetAdmin(admin.ModelAdmin):
    form = InstructionSetFormAdmin

    def duplicate_set(self, request, queryset):
            '''
            duplicate instruction set
            '''
            if queryset.count() != 1:
                  self.message_user(request,"Select only one instruction set to copy.", messages.ERROR)
                  return

            base_instruction_set = queryset.first()

            instruction_set = InstructionSet()
            instruction_set.save()
            instruction_set.copy_pages(base_instruction_set.instructions)

            self.message_user(request,f'{base_instruction_set} has been duplicated', messages.SUCCESS)

    duplicate_set.short_description = "Duplicate Instruction Set"

    inlines = [
        InstructionPageInline,
      ]
    
    actions = [duplicate_set]

