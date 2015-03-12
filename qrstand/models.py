from django.db import models
from django.utils import timezone
from django.db.models import F

class Stand(models.Model):
    sid = models.IntegerField(verbose_name='Stand Id')
    top_scan_count = models.IntegerField(default=0, verbose_name='# scans in the top')
    bottom_scan_count = models.IntegerField(default=0, verbose_name='# scans in the bottom')
    def __unicode__(self):
        return 'Stand %s' % self.sid
    def reset(self, request):
        self.top_scan_count = 0
        self.bottom_scan_count = 0
        self.save()
        self.log(request, Log.RESET)
    def empty(self, request, location):
        if location == 'U':
            self.bottom_scan_count = F('bottom_scan_count')+1
        elif location == 'D':
            self.top_scan_count = F('top_scan_count')+1
        self.save()
        self.log(request, location)
    def log(self, request, type):
        statement = Log(stand=self, action=type, ip=request.META['REMOTE_ADDR'])
        statement.save()

class Log(models.Model):
    stand = models.ForeignKey(Stand)
    created = models.DateTimeField(default=timezone.now,editable=False)
    RESET = 'RE'
    TOP_EMPTY = 'U'
    BOTTOM_EMPTY = 'D'
    ACTIONS = (
        (RESET, 'Reset'),
        (TOP_EMPTY, 'Top empty'),
        (BOTTOM_EMPTY, 'Bottom empty'),
    )
    action = models.CharField(max_length=2, choices=ACTIONS)
    ip = models.GenericIPAddressField()
