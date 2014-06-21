from django.db import models
from topnotchdev import files_widget
from django.core.exceptions import ObjectDoesNotExist
import calendar
import hashlib
import random
import datetime
from django.utils import timezone

class Show(models.Model):
    name = models.CharField(max_length=200, verbose_name = 'Title')
    last_modified = models.DateTimeField(auto_now_add=True,auto_now=True)
    last_sync = models.BigIntegerField(default=1)
    def __unicode__(self):
        return self.name
    def getSlides(self):
        relatedSlidegroups = self.slidegroup_set.all()
        resultingSlides = []
        for slidegroup in relatedSlidegroups:
            slides = slidegroup.photos.all()
            for slide in slides:
                element = {
                          'time': slidegroup.duration,
                          'uri': slide,
                          }
                resultingSlides.append(element)
        return resultingSlides
    def getDevices(self):
        relatedDevices = self.device_set.all()
        resultingList = []
        for device in relatedDevices:
            resultingList.append(device)
        return resultingList
    def setActiveOnAllDevices(self):
        Device.objects.all().update(active_show=self.id)
    def getSync(self):
        return self.last_sync
    class Meta:
        ordering = ('name',)
    def setSync(self, delta=20):
        self.last_sync = calendar.timegm(timezone.now().timetuple())+delta;
        self.save()

class SlideGroup(models.Model):
    series = models.ForeignKey(Show)
    photos = files_widget.ImagesField(verbose_name = 'Slides')
    duration = models.SmallIntegerField(default=5, verbose_name = 'Duration / s')
    last_modified = models.DateTimeField(auto_now_add=True,auto_now=True)
    def __unicode__(self):
        return u''

class Resolution(models.Model):
    y = models.SmallIntegerField(verbose_name='Height / px')
    x = models.SmallIntegerField(verbose_name='Width / px')
    def __unicode__(self):
        return u'%d x %d' % ( self.x, self.y )
    class Meta:
        ordering = ('-x',)

class Device(models.Model):
    def generateApiKey():
        randomBits = random.getrandbits(256)
        hashed = hashlib.sha224(str(randomBits)).hexdigest()
        return hashed    
    name = models.CharField(max_length=200, verbose_name = 'Device name')
    last_modified = models.DateTimeField(auto_now_add=True,auto_now=True)
    active_show = models.ForeignKey(Show, on_delete=models.PROTECT)
    api_key = models.CharField(max_length=200, default = generateApiKey)
    resolution = models.ForeignKey(Resolution, on_delete = models.PROTECT)
    last_ping = models.DateTimeField()
    def __unicode__(self):
        return self.name
    def getResolution(self):
        return u'%dx%d' % (self.resolution.x, self.resolution.y)
    def getSlideshow(self):
        return self.active_show
    def getLastModifiedTimestamp(self):
        return calendar.timegm(self.last_modified.timetuple())
    def getLogMessages(self):
        #relatedDevices = self.devicelog_set.all()
        #resultingList = []
        #for message in relatedLogs:
        #    resultingList.append(device)
        #return resultingList
        pass
    def isActive(self):
        # A device is inactive if it
        # has not pinged in 30 seconds.
        time = self.last_ping + datetime.timedelta(seconds=30)
        if time > timezone.now():
            return True
        else:
            return False
    def setActive(self):
        self.last_ping = timezone.now()
        self.save()
    is_active = property(isActive)
    class Meta:
        ordering = ('name',)

class DeviceLog(models.Model):
    device = models.ForeignKey(Device)
    network_interfaces = models.TextField(null=True, blank=True)
    
    date = models.DateTimeField()
    remote_ip = models.CharField(max_length=40)
    remote_host = models.CharField(max_length=255)
    
    levelno = models.IntegerField()
    levelname = models.CharField(max_length=255)
    
    name = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    pathname = models.CharField(max_length=255)
    funcName = models.CharField(max_length=255)
    lineno = models.IntegerField()
    
    msg = models.TextField()
    exc_info = models.TextField(null=True, blank=True)
    exc_text = models.TextField(null=True, blank=True)
    args = models.TextField(null=True, blank=True)
    
    threadName = models.CharField(max_length=255)
    thread = models.FloatField()
    created = models.FloatField()
    process = models.IntegerField()
    relativeCreated = models.FloatField()
    msecs = models.FloatField()
    class Meta:
        ordering = ('-date',)
    def __unicode__(self):
        return '%s: %s' % (self.date, self.formatMessage())
    def _get_short_msg(self):
        msg = self.msg[0:60] 
        if len(self.msg) > 60:
            msg += '...'
        return msg
    short_msg = property(_get_short_msg)
    def formatMessage(self):
        msg = self.msg
        if len(self.args) > 2:
            msg = msg.replace('%d', '%s')
            msg = msg.replace('%f', '%s')
            withoutParen = self.args[1:-2]
            # Split by comma and remove whitespace
            arg = [x.strip() for x in withoutParen.split(',')]
            return msg % tuple(arg)
        return msg
    formatted_message = property(formatMessage)
