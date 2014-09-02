from django.views import generic
from models import Announcement
from django.core.urlresolvers import reverse
from fiber.views import FiberPageMixin
from django.utils import timezone


########################
## Announcement Views ##
########################


class AnnouncementView(FiberPageMixin, generic.ListView):
    template_name = 'base/home.html'
    context_object_name = 'announcement_list'

    def get_queryset(self):
        """Return a list of current announcements"""
        now = timezone.now()
        return Announcement.objects.filter(pub_date__lte=now).\
            filter(expires__gt=now).filter(approved=True).order_by('-pub_date', '-created')

    def get_fiber_page_url(self):
        return reverse('base:home')


class AnnouncementDetailView(FiberPageMixin, generic.DetailView):
    template_name = 'base/detail.html'
    model = Announcement

    # A class to combine the context for the fiber page with the general context.
    def get_fiber_page_url(self):
        return reverse('base:announcement_detail_root')


#####################
## Join Page Views ##
#####################

class JoinIndexView(FiberPageMixin, generic.ListView):
    # A class to combine the context for the fiber page with the general context.
    def get_fiber_page_url(self):
        return reverse('base:join')


class JoinView(JoinIndexView):
    template_name = 'base/join.html'
    context_object_name = 'announcement_list'

    def get_queryset(self):
        """Return a list of current announcements"""
        now = timezone.now()
        return Announcement.objects.filter(pub_date__lte=now).\
            filter(expires__gt=now).filter(approved=True).order_by('-pub_date')
