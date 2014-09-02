from django.test import TestCase
from base.models import Announcement
from fiber.models import Page
from django.core.urlresolvers import reverse
from django.utils import timezone
import datetime
from django.contrib.auth.models import User


class MockRequest(object):
    pass


class MockSuperUser(object):
    def has_perm(self, perm):
        return True

request = MockRequest()
request.user = MockSuperUser()

# Factory method to create a fiber page tree.
def create_django_page_tree():
    mainmenu=Page(title='mainmenu')
    mainmenu.save()
    home = Page.objects.create(title='home', parent=mainmenu, url='home', template_name='base/home.html')
    detail = Page.objects.create(title='detail', parent=home, url='home/detail', template_name='base/detail.html')
    join = Page.objects.create(title='join', parent=home, url='join', template_name='base/join.html')
    members = Page.objects.create(title='members', parent=home, url='members', template_name='base/members.html')
    meetings = Page.objects.create(title='meetings', parent=mainmenu, url='meetings', template_name='')


class AnnouncementMethodTests(TestCase):
    def test_create_announcement(self):
        announcements_starting_count = Announcement.objects.count()
        Announcement.objects.create(title="Test Title",
                                    short_title="Test_Short_Title",
                                    body="<p>Announcement body text html format</p>",
                                    category="Job",
                                    priority=1,
                                    expires=timezone.now()+datetime.timedelta(days=1),
                                    approved=True,
                                    )
        announcements_end_count = Announcement.objects.count()
        self.assertEqual(announcements_end_count, announcements_starting_count+1)

    def test_announcements_is_active_method(self):
        announcements_starting_count = Announcement.objects.count()
        Announcement.objects.create(title="Test Active Announcement",
                                    short_title="Test_Short_Title",
                                    body="<p>Announcement body text html format</p>",
                                    category="Job",
                                    priority=1,
                                    expires=timezone.now()+datetime.timedelta(days=1),  # current announcement
                                    approved=True,
                                    )
        Announcement.objects.create(title="Test Expired Announcement",
                                    short_title="Test_Short_Title",
                                    body="<p>Announcement body text html format. To be or not to be that is the"
                                         "question. Whether t'is nobler in the mind to suffer the slings and arrows"
                                         "of outrageous fortune or to take arms against a sea of troubles and by "
                                         "opossing end them.</p>",
                                    category="Job",
                                    priority=1,
                                    expires=timezone.now()+datetime.timedelta(days=-1),  # expired announcement
                                    approved=True,
                                    )
        announcements_end_count = Announcement.objects.count()
        self.assertEqual(announcements_end_count, announcements_starting_count+2)
        announcement = Announcement.objects.get(title="Test Active Announcement")
        self.assertEqual(announcement.pk, 1)
        self.assertEqual(announcement.is_active(), True)  # should be true b/c pub_date current, approved, not expired
        expired_announcement = Announcement.objects.get(title="Test Expired Announcement")
        self.assertEqual(expired_announcement.is_active(), False)  # Should return False

        # create different pub dates
        old_pub_datetime = timezone.now()+datetime.timedelta(days=-2)
        old_pub_date = old_pub_datetime.date()
        future_pub_datetime = timezone.now()+datetime.timedelta(days=+2)
        future_pub_date = future_pub_datetime.date()
        # Test is active method with different pub dates
        announcement.pub_date = old_pub_date  # current announcement has older pub date
        self.assertEqual(announcement.is_active(), True)  # past or current pub date should be active
        announcement.pub_date = future_pub_date
        self.assertEqual(announcement.is_active(), False)  # future pub date should not be active
        announcement.pub_date = old_pub_date
        self.assertEqual(announcement.is_active(), True)  # return to good pub date, should be true
        announcement.approved = False
        self.assertEqual(announcement.is_active(), False)  # OK pub date, but not approved
        # Test body_header method
        self.assertEqual(expired_announcement.body_header(), "<p>Announcement body text html format. To be or no")
        self.assertEqual(len(expired_announcement.body_header()), 50)


class PageViewTests(TestCase):
    """
    Tests for the pages and links in the base part of the site, including the home page,
    and announcement detail pages, the join page and the members search page.
    """

    def test_home_page_view(self):
        create_django_page_tree()  # create a test fiber page tree
        self.assertEqual(reverse('base:home'), '/home/')  # sanity check for reverse method
        response = self.client.get(reverse('base:home'))  # fetch the home page
        self.assertEqual(response.status_code, 200)  # check home page returns 200
        self.assertContains(response, "There are no active announcements")  # Test no announcements message
        Announcement.objects.create(title="A Wonderful Test Announcement",
                                    short_title="Test_Short_Title",
                                    body="<p>Announcement body text html format</p>",
                                    category="Job",
                                    priority=1,
                                    expires=timezone.now()+datetime.timedelta(days=1),  # current announcement
                                    approved=True,)
        response = self.client.get(reverse('base:home'))
        self.assertContains(response, "A Wonderful Test Announcement")  # Test that announcement appears on home page

    def test_announcement_detail_page_veiw(self):
        create_django_page_tree()  # create a test fiber page tree
        # sanity check for reverse
        self.assertEqual(reverse('base:announcement_detail', kwargs={'pk': 1}), '/home/detail/1/')
        self.assertEqual(reverse('base:announcement_detail_root'), '/home/detail/')
        # create an announcement
        Announcement.objects.create(title="A Wonderful Test Announcement",
                                    short_title="Test_Short_Title",
                                    stub="A brief announcement stub",
                                    body="""<p>Announcement body text html format.
                                    The long and winding road takes me home. To the place
                                     I want to be. And as we wind on down the road. Our
                                     shadows taller than our souls.</p>""",
                                    category="Job",
                                    priority=1,
                                    expires=timezone.now()+datetime.timedelta(days=1),  # current announcement
                                    approved=True,)
        a = Announcement. objects.get(title="A Wonderful Test Announcement")
        self.assertEqual(reverse('base:announcement_detail', args=[a.id]), '/home/detail/'+str(a.id)+"/")
        response = self.client.get(reverse('base:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A Wonderful Test Announcement")
        self.assertContains(response, "more...")

        # TODO Add a detail view test
        # Detail page view tests raise a key error from fiber when the is_public_for_user method is called on the fiber
        # page. This method takes a user argument which is passed, somehow, on the working web page, but is not
        # passed by the test client!


    def test_reverse_method_for_join_page(self):
        create_django_page_tree()
        response = self.client.get(reverse('base:join'))
        self.assertEqual(response.status_code, 200)