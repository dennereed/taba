from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField
import os
from choices import ANNOUNCEMENT_CHOICES
from django.core.urlresolvers import reverse


############################################
# PaleoanthroUser
############################################

class TabaUser(models.Model):
    """
    This class "extends" the default Django user class. It adds TABA
    specific fields to the user database, allowing us to use the auth
    system to track and manage paleocore users rather than constructing a separate
    membership database.

    This class is coupled with a custom PaleoCoreUserAdmin module in base.admin.py
    """
    user = models.OneToOneField(User)

    # other fields
    institution = models.CharField(max_length=255, null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    send_emails = models.BooleanField(default=True)

    def __unicode__(self):
        return self.user.first_name + " " + self.user.last_name

    class Meta:
        db_table = "taba_user"
        verbose_name_plural = "User Info"
        verbose_name = "User Info"
        ordering = ["user__last_name", ]


class Announcement(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, null=False, blank=False)
    short_title = models.CharField(max_length=50, null=False, blank=False)
    stub = RichTextField()
    body = RichTextField(null=True, blank=True)
    category = models.CharField(max_length=20, choices=ANNOUNCEMENT_CHOICES)
    priority = models.IntegerField()
    created = models.DateField(default=timezone.now())
    pub_date = models.DateField(default=timezone.now())  # field type converts datetime to date
    expires = models.DateField()
    approved = models.NullBooleanField()
    upload1 = models.FileField(upload_to='uploads/files', null=True, blank=True)
    upload2 = models.FileField(upload_to='uploads/files', null=True, blank=True)
    upload3 = models.FileField(upload_to='uploads/files', null=True, blank=True)

    def __unicode__(self):
        return self.title[0:20]

    def body_header(self):
        return self.body[0:50]

    def is_active(self):
        now = timezone.now().date()   # need current date (rather than datetime) for comparison
        return self.expires > now and self.pub_date <= now and self.approved is True
    is_active.admin_order_field = 'pub_date'
    is_active.boolean = True
    is_active.short_description = 'Active'

    def get_absolute_url(self):
        return reverse('announcement_detail', kwargs={'pk': self.id})

    @property
    def upload1_filename(self):
        return os.path.basename(self.upload1.name)

    def upload2_filename(self):
        return os.path.basename(self.upload2.name)

    def upload3_filename(self):
        return os.path.basename(self.upload3.name)
