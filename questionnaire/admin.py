from django import forms
from django.contrib import admin
from slideshow.models import Show
from questionnaire.models import Survey, Response, Answer, Participant, TextMessage, TextMessageLog
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.conf.urls import patterns, url
from django.core.exceptions import ValidationError
from admin_buttons import ButtonAdmin
from django.contrib.admin.actions import delete_selected

class SurveyAdminForm(forms.ModelForm):
    model = Survey
    class Media:
        # JS for counting characters on text message field.
        js = ( 'questionnaire/js/jquery.character-counter.jquery.js', 'questionnaire/js/jquery.character-counter.js', )
    def __init__(self, *args, **kwargs):
        super(SurveyAdminForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['style'] = 'width:610px;'
        self.fields['text_message'].widget = forms.Textarea(attrs={'rows':3, 'cols':40})
        self.fields['text_message'].widget.attrs['style'] = 'width:610px;'
        self.fields['text_message'].widget.attrs['class'] = 'counted'
    def clean(self):
        cleaned_data = super(SurveyAdminForm, self).clean()
        # The text message has to contain the code.
        if '%s' not in self.cleaned_data['text_message'] and self.cleaned_data['text_message'] != '':
            msg = 'The code denoted by %s has to be in the text message.'
            self._errors['text_message'] = self.error_class([msg])
            del cleaned_data['text_message']
        # If the instance has responses then its markup cannot be changed
        if self.instance.hasResponse() and "markup" in self.changed_data:
            msg = 'You cannot edit the markup of a survey that has existing responses.'
            self._errors['markup'] = self.error_class([msg])
            del cleaned_data['markup']
        # If this instance is being edited, it is the only one and it is being set to inactive then alert the user.
        if self.instance.pk and self.cleaned_data['active'] is False and Survey.objects.count() is 1:
            msg = 'At least one object has to be active.'
            self._errors['active'] = self.error_class([msg])
            del cleaned_data['active']
        return cleaned_data

class SurveyAdmin(admin.ModelAdmin):
    form = SurveyAdminForm
    save_as = True
    def setActiveLink(self):
        url = reverse('admin:setActive', args=[self.id])
        return u"<a href='%s'>Activate</a>" % url
    setActiveLink.short_description = ''
    setActiveLink.allow_tags = True
    def viewSurveyLink(self):
        url = reverse('questionnaire:survey', args=[self.id])
        return u"<a href='%s' target='_blank'>View survey</a>" % url
    viewSurveyLink.short_description = ''
    viewSurveyLink.allow_tags = True
    def exportSurveyLink(self):
        url = reverse('questionnaire:export', args=[self.id])
        return u"<a href='%s' target='_blank'>Export survey responses</a>" % url
    exportSurveyLink.short_description = ''
    exportSurveyLink.allow_tags = True
    def setActive(self, request, surveyId):
        survey = get_object_or_404(Survey, pk=surveyId)
        survey.setActive()
        return redirect(reverse('admin:questionnaire_survey_changelist'))
    def nResponses(self):
        return self.numberOfResponses()
    nResponses.short_description = 'Responses'
    list_display = ('name', nResponses, viewSurveyLink, 'active', setActiveLink, exportSurveyLink)
    
    def get_urls(self):
        urls = super(SurveyAdmin, self).get_urls()
        newUrls = patterns('',
                           url(
                               r'set_active/(?P<surveyId>\d+)/$',
                               self.admin_site.admin_view(self.setActive),
                               name = 'setActive',
                               ),
                  )
        return newUrls+urls

admin.site.register(Survey, SurveyAdmin)

class AnswerInline(admin.TabularInline):
    def has_add_permission(self, request):
        return False
    verbose_name = "Answer"
    model = Answer
    readonly_fields = ('question','tanswer',)
    extra = 0
    order_by = ('question_id',)
    exclude = ('question_id', 'answer',)
    can_delete = False

class ResponseAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    def _survey(self):
        url = reverse('admin:questionnaire_survey_change',args=[self.survey_id])
        return u"<a href='%s'>%s</a>" % (url, self.survey)
    _survey.allow_tags = True
    inlines = [AnswerInline]
    exclude = ('survey',)
    readonly_fields = (_survey, )
    list_filter = ('survey',)
    list_display = ('survey', 'created',)
    
admin.site.register(Response, ResponseAdmin)

class ParticipantAdmin(ButtonAdmin):
    readonly_fields = ('name',)
    def clearLogs(self, request):
        # Deletes all log entries
        result = Participant.objects.all()
        action = delete_selected(self, request, result)
        if action is None:
            return redirect(reverse('admin:questionnaire_participant_changelist'))
        else:
            return action
    clearLogs.short_description = 'Clear participants'
    list_buttons = [clearLogs]
    def has_add_permission(self, request, obj=None):
        return False
admin.site.register(Participant, ParticipantAdmin)

class TextMessageLogInline(admin.TabularInline):
    def has_add_permission(self, request):
        return False
    verbose_name = "Log message"
    model = TextMessageLog
    readonly_fields = ('created', 'message_id',)
    extra = 0
    order_by= ('created',)
    can_delete = False

class TextMessageAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    inlines = [TextMessageLogInline]
    verbose_name = "Text Message"
    readonly_fields = ('participant','code', 'created','uuid',)
    order_by = ('created',)
    list_filter = ('active',)
    def deactivateLink(self):
        url = reverse('admin:setInactive', args=[self.id])
        return u"<a href='%s'>Deactivate</a>" % url
    deactivateLink.short_description = ''
    deactivateLink.allow_tags = True
    def setInactive(self, request, textMessageId):
        text_message = get_object_or_404(TextMessage, pk=textMessageId)
        text_message.setInactive()
        return redirect(reverse('admin:questionnaire_textmessage_changelist'))
    list_display = ('code', 'active', 'created',deactivateLink,)

    def get_urls(self):
        urls = super(TextMessageAdmin, self).get_urls()
        newUrls = patterns('',
                           url(
                               r'set_inactive/(?P<textMessageId>\d+)/$',
                               self.admin_site.admin_view(self.setInactive),
                               name = 'setInactive',
                               ),
                  )
        return newUrls+urls
admin.site.register(TextMessage, TextMessageAdmin)
