from django.http import HttpResponse, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django import forms
from django.utils.html import mark_safe
from django.utils.text import slugify
from questionnaire.models import Survey, Response, Answer, Participant, TextMessage, TextMessageLog
from django.shortcuts import get_object_or_404
import cups
from django.conf import settings
import urllib, urllib2
from bs4 import BeautifulSoup
import csv
import ast
from django.contrib.auth.decorators import login_required

class SurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields')
        survey = kwargs.pop('survey')
        super(SurveyForm, self).__init__(*args, **kwargs)
        if survey.text_message != '':
            self.fields['participant_phone'] = forms.IntegerField(
                                               widget=forms.TextInput,
                                               required=False,
                                               min_value = 10000000,
                                               max_value = 99999999,
                                               label='What is your mobile phone number? (optional)',
                                               help_text = "We use this to send you a confirmation code via. text message which is needed to redeem your prize. You will not be able to redeem your prize if you do not give us your mobile phone number. We do not store your phone number."
                                               )
        for i, value in fields.iteritems():
            field = None
            help = None
            question = mark_safe(value['question'])
            if 'help' in value:
                help = mark_safe(value['help'])
            if value['type'] == 'text':
                field = forms.CharField(label=question, required=value['required'], help_text=help)
            elif value['type'] == 'textarea':
                field = forms.CharField(widget=forms.Textarea, label=question, required=value['required'], help_text=help)
            elif value['type'] == 'radio':
                field = forms.ChoiceField(widget=forms.RadioSelect, label=question, required=value['required'], choices=value['choices'], help_text=help)
            elif value['type'] == 'checkboxgroup':
                field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label=question, required=value['required'], choices=value['choices'], help_text=help)
            elif value['type'] == 'html':
                field = forms.CharField(label='html', help_text=question, required=False)
            if field is not None:
                # Give the field a tag so that we know we added it.
                if 'id' in value:
                    id = '%s' % value['id']
                elif value['type'] == 'html':
                    id = 'html_%s' % i
                else:
                    id = 'q_%s' % i
                self.fields[id] = field;
    def answers(self):
        for name, value in self.cleaned_data.items():
            # Find the dynamically generated fields.
            if name.startswith('q_'):
                yield (name[2:], value)

def index(request):
    # If there is just one questionnaire then show it.
    # Otherwise get the one marked as active.
    if Survey.objects.count() == 1:
        id = Survey.objects.all()[:1].id
    else:
        id = Survey.objects.filter(active=True)[0].id
    return redirect(reverse('questionnaire:survey', kwargs={'survey_id': id}))

class Question():
    def __init__(self, id, question):
        self.id = id
        self.question = question.encode('latin1')
        self.answers = []
        self.subquestions = []
    def answer(self, answer):
        if isinstance(answer, basestring):
            answer = answer.encode('latin1')
        self.answers.append(answer)
    def subquestion(self, obj):
        self.subquestions.append(obj)
    def __unicode__(self):
        return self.question
    def getAnswers(self):
        return self.answers

@login_required
def export(request, survey_id):
    if request.user.is_authenticated() is not True:
        return httpResponseForbidden()
    survey = get_object_or_404(Survey, id=survey_id)
    # If there are no responses then don't bother
    if survey.response_set.count() is 0:
        return HttpResponseServerError()
    
    responses = survey.getResponses()
    
    # Create a list of Question objects
    # The questions will be identical on each
    # response.
    questions = {}
    q = survey.getQuestions()
    for i, value in q.iteritems():
        question = value['question']
        questions[i] = Question(i, question)
        if value['type'] in ('radio', 'checkboxgroup',):
            for ii, option in value['choices']:
                iii = "%s.%s" % (i, ii)
                questions[iii] = Question(iii, option)
                questions[i].subquestion(questions[iii])
    
    # Attach answers from responses to questions
    for response in responses:
        for i, value in response.iteritems():
            type, question, answer = value
            # Convert ID strings to lists of IDs
            if type == 'checkboxgroup':
                chosen_option_ids = ast.literal_eval(answer)
            elif type == 'radio':
                chosen_option_ids = [answer]
            # Mark the ones chosen with a 1
            # and the rest with a 0.
            if type in ('radio', 'checkboxgroup',):
                chosen_option_ids = ["%s.%s" % (i, x) for x in chosen_option_ids]
                for q in questions[i].subquestions:
                    if q.id in chosen_option_ids:
                        q.answer(1)
                    else:
                        q.answer(0)
            else:
                questions[i].answer(answer)

    # Prepare a CSV file for download.
    response = HttpResponse(content_type='text/csv')
    filename = slugify(survey.name)
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename
    # Custom delimiter compensates for differences
    # in Excel in english versus danish.
    writer = csv.writer(response, delimiter=';')
    # Order by question ID so they appear in the
    # same order as in the markup.
    result = sorted(questions.items(), key = lambda x: float(x[1].id))
    # Write a header row, then the data.
    writer.writerow([survey.name])
    writer.writerow(['Question ID', 'Question', 'Answers'])
    writer.writerow(['', 'Submission date']+[e.created.strftime('%d-%m-%Y') for e in survey.response_set.all()])
    rows = [[question.id, question.question]+question.getAnswers() for i, question in result]
    writer.writerows(rows)
    #for i, question in result:
    #    writer.writerow([question.id, question.question]+question.getAnswers())
    return response

def survey(request, survey_id):
    # 404 if the survey doesn't exist.
    survey = get_object_or_404(Survey, id=survey_id)
    # Does a receipt for printing exist?
    receipt = len(str(survey.receipt))
    # Build the form
    fields = survey.getQuestions()
    form = SurveyForm(request.POST or None, fields = fields, survey = survey)
    if form.is_valid():
        response = Response(survey=survey)
        response.save()
        for (question, answer) in form.answers():
            response.answer_set.create(question_id=question, answer=answer)
        confirmation = survey.getConfirmation()
        if receipt:
            # Do the printing
            path = survey.receipt.path
            printer = cups.Connection()
            printer.printFile(settings.QUESTIONNAIRE_PRINTER, path, 'Questionnaire receipt', {})
        # Does participant already exist?
        participant = Participant()
        #if participant.doesParticipantExist(form.cleaned_data['participant_phone']):
        #    pass #If the participant exists already then abort.
        if 'participant_name' in request.POST and request.POST['participant_name'] is not u'':
            participant.name = form.cleaned_data['participant_name']
            participant.save()
        if 'participant_phone' in request.POST and request.POST['participant_phone'] is not u'':
            participant.phone = form.cleaned_data['participant_phone']
            participant.save()
            text_message = TextMessage()
            text_message.participant = participant
            text_message.save()
            text = survey.text_message % str(text_message.code)
            data = {
                'username': 'studerende',
                'password': settings.SMS_PASSWORD,
                'recipient': '45' + str(form.cleaned_data['participant_phone']),
                'text': text,
                'from': 'DSE',
                'callback': 'http://esf.studerende.dk'+reverse('questionnaire:callback'),
                'reply': 'extended',
                    }
            # Send the text message and parse the response.
            xmlresponse = urllib2.urlopen('https://api.sms1919.dk/rpc/push/', urllib.urlencode(data)).read()
            soup = BeautifulSoup(xmlresponse)
            sms_id = soup.result.messageid.contents
            text_message.uuid = "".join(unicode(item) for item in sms_id)
            text_message.save()
        context = {'name': survey.name, 'confirmation': mark_safe(confirmation), 'receipt': receipt}
        return render(request, 'questionnaire/confirmation.html', context)

    introduction = survey.getIntroduction()
    context = {'name': survey.name, 'introduction': mark_safe(introduction), 'form': form}
    return render(request, 'questionnaire/form.html', context)

class CallbackForm(forms.Form):
    messageid = forms.CharField(max_length=100)
    status = forms.IntegerField(min_value = 0, max_value = 1000)

def callback(request):
    form = CallbackForm(request.GET)
    if form.is_valid():
        current_text_message = TextMessage.objects.get(uuid=form.cleaned_data['messageid'])
        log_entry = TextMessageLog(text_message=current_text_message, message_id = form.cleaned_data['status'])
        log_entry.save()
        return HttpResponse('')
    return HttpResponseServerError()
