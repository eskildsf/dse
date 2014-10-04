from django.db import models
from django.utils import timezone
from bs4 import BeautifulSoup
import re
import ast
from django.db.models.signals import post_delete
from django.dispatch import receiver
import uuid
import hashlib
from collections import OrderedDict

def today():
    # Returns a datetime object that is timezone
    # aware and only includes the date.
    date = timezone.now().replace(hour=12, minute=12, second=12, microsecond=12)
    return date

def c(l):
    return "".join(unicode(item) for item in l.contents)

def clean(s):
    regex = re.compile(r'[\n\r\t]')
    return regex.sub("", s.strip())

class Survey(models.Model):
    name = models.CharField(max_length=200, verbose_name = 'Title')
    markup = models.TextField()
    active = models.BooleanField(default=False)
    receipt = models.FileField(upload_to='questionnaire', blank = True, help_text = 'A receipt will only be printed if one is specified.')
    text_message = models.CharField(max_length=255, verbose_name = 'Confirmation text message', blank = True, help_text = 'A text message will only be sent if this field is not left blank.')
    def __unicode__(self):
        return self.name
    def save(self, *args, **kwargs):
        # Only one can be active at a time.
        if self.active:
            currently_active = Survey.objects.update(active=False)
        # If this is the only object then it HAS to be active
        if Survey.objects.count() == 1:
            self.active = True
        return super(Survey, self).save(*args, **kwargs)
    def setActive(self):
        self.active = True
        self.save()
    def hasResponse(self):
        return self.response_set.count() > 0
    def getQuestions(self):
        soup = BeautifulSoup(self.markup)
        # These are the accepted fields:
        types = ('text', 'textarea', 'radio', 'checkboxgroup', 'html',)
        fields = OrderedDict()
        survey = soup.questionnaire.contents
        # Only loop through actual fields
        gen = ( x for x in survey if hasattr(x, 'name') and x.name in types )
        for i, child in enumerate(gen):
            question = c(child).replace('\n', '')
            type = child.name
            options = None
            if child.name in ('radio', 'checkboxgroup',):
                options = question.split('* ')
                question = options.pop(0)
                choices = []
                for ii, option in enumerate(options, start=1):
                    choices.append((str(ii), clean(option),))
                options = tuple(choices)
            required = child.has_attr('required')
            question = clean(question)
            field = {'question': question, 'type': type, 'choices': options, 'required': required}
            if child.has_attr('id'):
                field['id'] = child.get('id')
            if child.has_attr('help'):
                field['help'] = child.get('help')
            fields[str(i)] = field
        return fields
    def getIntroduction(self):
        soup = BeautifulSoup(self.markup)
        return c(soup.questionnaire.introduction)
    def getConfirmation(self):
        soup = BeautifulSoup(self.markup)        
        return c(soup.questionnaire.confirmation)
    def getResponses(self):
        if self.response_set.count() == 0:
            return []
        questions = self.getQuestions()
        responses = self.response_set.all()
        result = []
        for response in responses:
            response.c_questions = questions
            result.append(response.getQuestionsAndAnswers())
        return result

# If there will be just one survey left after a delete procedure
# then the last one has to be active.
@receiver(post_delete, sender = Survey, dispatch_uid = 'survey_delete_signal')
def check_active_survey_exists(sender, instance, using, **kwargs):
    if Survey.objects.count() == 1:
        surveys = Survey.objects.all()
        survey = surveys[:1].get()
        survey.setActive()

class Response(models.Model):
    survey = models.ForeignKey(Survey)
    created = models.DateTimeField(editable=False)
    def __unicode__(self):
        return self.survey.name+' on the '+unicode(self.created.replace(microsecond=0))
    def save(self, *args, **kwargs):
        if not self.id:
            self.created = today()
        else:
            pass
        super(Response, self).save(*args, **kwargs)
    def getQuestionsAndAnswers(self):
        if hasattr(self, 'c_questions'):
            questions = self.c_questions
        else:
            questions = self.survey.getQuestions()
            self.c_questions = questions
        answers = self.answer_set.all()
        result = {}
        for e in answers:
            e.c_field = questions[e.q_id()]
            result[e.q_id()] = (e.type(), e.question(), e.answer)
        return result

class Answer(models.Model):
    response = models.ForeignKey(Response)
    question_id = models.SmallIntegerField()
    answer = models.TextField()
    def __unicode__(self):
        return self.field()['type'].title()
    def q_id(self):
        return str(self.question_id)
    def field(self):
        if hasattr(self, 'c_field'):
            return self.c_field
        field = self.response.survey.getQuestions()[self.q_id()]
        self.c_field = field
        return field
    def type(self):
        return self.field()['type']
    def question(self):
        return self.field()['question']
    question.short_description = 'Question'
    def tanswer(self):
        if self.field()['type'] == 'radio':
            r = self.field()['choices'][int(self.answer)-1][1]
        elif self.field()['type'] == 'checkboxgroup':
            chosen_option_ids = ast.literal_eval(self.answer)
            chosen_options = [self.field()['choices'][int(x)-1][1] for x in chosen_option_ids]
            r = ', '.join(chosen_options)
        else:
            r = self.answer
        return r
    tanswer.short_description = 'Answer'
    class Meta:
        ordering = ['question_id']

class Participant(models.Model):
    created = models.DateTimeField(editable=False)
    phonehash = models.CharField(max_length=200, verbose_name = 'Tlf hash', editable = False, blank = True)
    name = models.CharField(max_length=200, verbose_name = 'Name', editable = False, blank = True)
    def __unicode__(self):
        if len(self.phonehash) > 7:
            return self.phonehash
        else:
            return self.name
    def save(self, *args, **kwargs):
        if not self.id:
            if hasattr(self, 'phone'):
                self.phonehash = hashlib.sha1(str(self.phone)).hexdigest()
            self.created = today()
        super(Participant, self).save(*args, **kwargs)
    def doesParticipantExist(self, phone, name):
        phonehash = hashlib.sha1(str(phone)).hexdigest()
        return Participant.objects.filter(phonehash=phonehash).count() is not 0        
    def canParticipantParticipate(self, phone, name):
        pass# When did the participant participate last time?
        # Did the participant get a survey gift?

class TextMessage(models.Model):
    participant = models.ForeignKey(Participant)
    created = models.DateTimeField(editable=False)
    uuid = models.CharField(max_length=200, verbose_name = 'sms1919 ID', editable = False, db_index = True)
    code = models.CharField(max_length=200, verbose_name = 'Code', editable = False, db_index = True)
    active = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        if not self.id:
            self.code = hash(str(uuid.uuid1())) % 1000000
        super(TextMessage, self).save(*args, **kwargs)
    def setInactive(self):
        self.active = False
        self.save()

class TextMessageLog(models.Model):
    created = models.DateTimeField(editable=False)
    text_message = models.ForeignKey(TextMessage)
    message_id = models.SmallIntegerField()
    def message(self):
        pass
