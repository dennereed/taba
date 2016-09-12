from django.test import TestCase
from models import Meeting, Abstract, Author
from django.core.urlresolvers import reverse
from fiber.models import Page


# Factory method to create a fiber page tree with five pages.
def create_django_page_tree():
    mainmenu=Page(title='mainmenu')
    mainmenu.save()
    home=Page(title='home', parent=mainmenu, url='home', template_name='base/home.html')
    home.save()
    # join=Page(title='join', parent=home, url='join', template_name='base/join.html')
    # join.save()
    # members=Page(title='members', parent=home, url='members', template_name='base/members')
    # members.save()
    meetings = Page(title='meetings', parent=mainmenu, url='meetings', template_name='')
    meetings.save()


# Factory methods to create test abstracts, meetings, and authors
def create_meeting(year=2020, title='Jamaica 2020', location='Jamaica', associated_with='AAPA'):
    """
    Creates a Meeting with default values for year, title, location and associated_with.
    """
    return Meeting(title, year, location=location,associated_with=associated_with)


# Factory method to create a fiber page tree with five base pages plus three meetings pages and their associated
# meeting instances.
def create_three_meetings_with_pages():
    # Create base fiber tree
    create_django_page_tree()
    # Create meeting instances
    calgary = Meeting(year=2014, title='Calgary 2014', location='Calgary, AB', associated_with='AAPA')
    calgary.create_fiber_page()
    calgary.save()
    san_francisco = Meeting(year=2015, title='San Francisco 2015', location='San Francisco, CA', associated_with='SAA')
    san_francisco.create_fiber_page()
    san_francisco.save()
    atlanta = Meeting(year=2016, title='Atlanta 2016', location='Atlanta, GA', associated_with='AAPA')
    atlanta.create_fiber_page()
    atlanta.save()


def create_abstract(meeting,
                    contact_email='denne.reed@gmail.com',
                    presentation_type='Paper',
                    title='Silly Walks of the Neanderthals',
                    abstract_text="""<p> Test abstract text about silly walks in Neanderthals.</p> """,
                    year=2020):

    return Abstract(meeting, contact_email, presentation_type, title, abstract_text, year=year)


def create_author(abstract, author_rank,
                  last_name='Fake',
                  first_name="Ima",
                  name='Ima Fake',
                  department='Fake Anthropology',
                  institution='Chaos University',
                  country='United States of America',
                  email_address='denne.reed@gmail.com'
                  ):

    return Author(abstract, author_rank,
                  last_name=last_name,
                  first_name=first_name,
                  name=name,
                  department=department,
                  institution=institution,
                  country=country,
                  email_address=email_address
                  )


class MeetingMethodTests(TestCase):
    def test_meeting_create_fiber_page_method(self):
        """
        Tests the fiber page constructor method. The fiber page method get_absolute_url does
        not work as expected. Not sure why....
        """
        # Create a meeting
        calgary_2014 = Meeting(year=2014, title='Calgary 2014', location='Calgary', associated_with='AAPA')
        calgary_2014.save()
        # Create a default page tree
        create_django_page_tree()
        # Call page constructor method
        calgary_2014.create_fiber_page()
        # Fetch the fiber page we just created
        calgary_2014_fiber_page = Page.objects.get(url__exact='2014')
        # Test the attributes of the fiber page
        self.assertEqual(calgary_2014_fiber_page.parent, Page.objects.get(url__exact='meetings'))
        self.assertEqual(calgary_2014_fiber_page.url, '2014')
        self.assertEqual(calgary_2014_fiber_page.title, 'Calgary 2014')
        #self.assertEqual(calgary_2014_fiber_page.get_absolute_url, '/meetings/2014/') TODO Whys does this test fail?
        # Test that the page renders
        response = self.client.get('/meetings/2014/')
        self.assertEqual(response.status_code, 200)

    def test_meeting_has_detail_method(self):
        """
        Tests the has_detail method
        """
        # Create a meeting
        calgary_2014 = Meeting(year=2014, title='Calgary 2014', location='Calgary', associated_with='AAPA')
        calgary_2014.save()
        # Create a default page tree
        create_django_page_tree()
        # IF no fiber page then has_detail should be false
        self.assertEqual(calgary_2014.has_detail(), False)
        # Call page constructor method
        calgary_2014.create_fiber_page()
        # If fiber page then has_detail should be true
        self.assertEqual(calgary_2014.has_detail(), True)
        cfp = Page.objects.get(url__exact=2014)  # get tha page instance
        cfp.is_public = False  # set to not public
        cfp.save()  # save the change
        self.assertEqual(calgary_2014.has_detail(), False)  # Now has detail should return false


class MeetingsViewTests(TestCase):
    def test_meetings_index_view_with_no_meetings(self):
        create_django_page_tree()
        response = self.client.get(reverse('meetings:meetings'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['meeting_list'], [])

    def test_meetings_index_view_with_meetings(self):
        create_three_meetings_with_pages()  # Constructs fiber page tree with three meetings and associated pages
        response = self.client.get(reverse('meetings:meetings'))  # Meetings index should show three meetings
        calgary = Meeting.objects.get(year=2014)  # get meeting instance
        san_francisco = Meeting.objects.get(year=2015)
        atlanta = Meeting.objects.get(year=2016)
        self.assertContains(response, calgary.location, status_code=200,)
        self.assertContains(response, san_francisco.location, status_code=200)
        self.assertContains(response, atlanta.location, status_code=200)
        self.assertQuerysetEqual(response.context['meeting_list'],
                                 ['<Meeting: Atlanta 2016>',
                                  '<Meeting: San Francisco 2015>',
                                  '<Meeting: Calgary 2014>'])
        self.assertContains(response, "<table>")  # response includes a table element
        self.assertContains(response, '<a href="/meetings/2014/"')  # contains a link to the 2014 meeting detail
        self.assertContains(response, '<a href="/meetings/2015/"')
        self.assertContains(response, '<a href="/meetings/2016/"')
        self.assertEqual(Page.objects.count(), 6)  # should have 8 fiber pages
        self.assertEqual(Meeting.objects.count(), 3)  # should hav 3 meetings

        atlanta_fp = Page.objects.get(url__exact=2016)  # Get Atlanta fiber page
        atlanta_fp.is_public = False  # Set to not public
        atlanta_fp.save()  # save the change
        self.assertEqual(atlanta_fp.is_public, False)
        self.assertEqual(atlanta.has_detail(), False)  # meeting should NOT have detail
        self.assertEqual(atlanta_fp.show_in_menu, False)  # meeting fiber page should not be in menu
        response = self.client.get(reverse('meetings:meetings'))  # Reload the page!
        # If fiber page is not public and not in menu there should be no link to it
        self.assertNotContains(response, '<a href="/meetings/2016/"')

    def test_meetings_index_view_with_missing_meetings(self):
        create_three_meetings_with_pages()
        response = self.client.get(reverse('meetings:meetings'))
        # Returns page but does not contain a meeting that does not exist.
        self.assertNotContains(response, "Vancouver", status_code=200)
        self.assertContains(response, "<table>", status_code=200)  # contains a table listing meetings


class MeetingsDetailViewTests(TestCase):
    fixtures = ['fiber_data_160911.json', 'meetings_data.json']

    def test_meetings_detail_view(self):
        # Key Error for the next line likely indicates that the fiber page is missing
        response = self.client.get(reverse('meetings:meeting_detail', args=[2016]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create an Abstract")


class AbstractCreateViewTests(TestCase):
    # load test data that includes fiber pages, meetings, abstracts etc.
    fixtures = ['fiber_data_160911.json', 'meetings_data.json']

    def test_sanity(self):
        self.assertEqual(Meeting.objects.count(), 2)
        starting_abstract_count = Abstract.objects.count()
        self.assertEqual(starting_abstract_count, 5)
        starting_author_count = Author.objects.count()
        self.assertEqual(starting_author_count, 6)
        austin2016 = Meeting.objects.get(pk=1)
        self.assertEqual(austin2016.location, 'Austin, TX')
        new_abstract = Abstract(meeting_id=24, contact_email='denne.reed@gmail.com', presentation_type='Paper',
                                title='Silly Walks of the Neanderthals',
                                abstract_text="""<p> Test abstract text about silly walks in Neanderthals.</p> """,
                                year=2015)  # create a new abstract for the san francisco meeting
        new_abstract.save()
        new_author = Author(abstract=new_abstract, author_rank=1, first_name="Bob",
                            last_name="Reed", institution="University of Texas at Austin",
                            department="Anthropology", country="United States of America",
                            email_address="denne.reed@gmail.com")
        new_author.save()
        self.assertEqual(Abstract.objects.count(), starting_abstract_count+1)
        self.assertEqual(Author.objects.count(), starting_author_count+1)

    def test_abstract_create_view_with_get(self):
        """A get request should load a blank version of the form"""
        response = self.client.get(reverse('meetings:create_abstract'))
        self.assertEqual(response.status_code, 200)  # Response should be an HTML page with status code 200
        self.assertTemplateUsed(response, 'meetings/abstract.html')  # Response should render the abstract.html template
        self.assertContains(response, "<form")  # Test that the page loads a form
        self.assertContains(response, "<p>Author 1<br>")  # Test that the page contains an author formset
        self.assertContains(response, "input", count=34)  # Test that the page contains 34 input elements

    # def test_abstract_create_view_with_empty_post(self):
    #     response = self.client.post(reverse('meetings:create_abstract'), {})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'meetings/abstract.html')  # Response should render abstract.html template

    # def test_abstract_create_view_with_completed_form(self):
    #     self.assertEqual(Abstract.objects.filter(year=2015).count(), 0)  # initially no 2015 abstracts
    #     form_data = {
    #         'meeting': 24,
    #         'year': 2015,
    #         'presentation_type': 'Paper',
    #          'title': """<p>A test title with strange characters &part;13C and species names
    #          like <em>Australopithecus afarensis</em></p>""",
    #
    #          'abstract_text': """<p>You think water moves fast? You should see ice. It moves like it has a mind. Like it
    #          knows it killed the world once and got a taste for murder. After the avalanche, it took us a week to climb
    #          out. Now, I don't know exactly when we turned on each other, but I know that seven of us survived the
    #          slide... and only five made it out. Now we took an oath, that I'm breaking now. We said we'd say it was
    #          the snow that killed the other two, but it wasn't. Nature is lethal but it doesn't hold a candle to man.
    #          </p>""",
    #          'acknowledgements': 'I gratefully acknowledge the academy.',
    #          'contact_email': 'denne.reed@gmail.com',
    #          'confirm_email':  'denne.reed@gmail.com',
    #          'author_set-0-name': 'Denne Reed',
    #          'author_set-0-department': 'Anthropology',
    #          'author_set-0-institution': 'University of Texas at Austin',
    #          'author_set-0-country': 'United States of America',
    #          'author_set-0-email_address': 'denne.reed@gmail.com',
    #     }
    #     response = self.client.post(reverse('meetings:create_abstract'), form_data)
    #     self.assertEqual(response.status_code, 302)  # test that successful submit returns redirect
    #     self.assertEqual(response['Location'], 'http://testserver/meetings/abstract/thanks/')  # test redirect location
    #     self.assertEqual(Abstract.objects.filter(year=2015).count(), 1)  # verify that new abstract is saved
    # #
    # def test_abstract_with_missing_title(self):
    #     form_data = {
    #         'meeting': 24,
    #         'year': 2015,
    #         'presentation_type': 'Paper',
    #          #'title': """<p>A test title with strange characters &part;13C and species names
    #          #like <em>Australopithecus afarensis</em></p>""",
    #
    #          'abstract_text': """<p>You think water moves fast? You should see ice. It moves like it has a mind. Like it
    #          knows it killed the world once and got a taste for murder. After the avalanche, it took us a week to climb
    #          out. Now, I don't know exactly when we turned on each other, but I know that seven of us survived the
    #          slide... and only five made it out. Now we took an oath, that I'm breaking now. We said we'd say it was
    #          the snow that killed the other two, but it wasn't. Nature is lethal but it doesn't hold a candle to man.
    #          </p>""",
    #          'acknowledgements': 'I gratefully acknowledge the academy.',
    #          'contact_email': 'denne.reed@gmail.com',
    #          'confirm_email':  'denne.reed@gmail.com',
    #          'author_set-0-name': 'Denne Reed',
    #          'author_set-0-department': 'Anthropology',
    #          'author_set-0-institution': 'University of Texas at Austin',
    #          'author_set-0-country': 'United States of America',
    #          'author_set-0-email_address': 'denne.reed@gmail.com',
    #     }
    #     response = self.client.post(reverse('meetings:create_abstract'), form_data)
    #     self.assertEqual(response.status_code, 200)  # test that on submit we return the form again
    #     self.assertEqual(response.context_data['form'].errors['title'][0], u'This field is required.')
    #
    # def test_abstract_with_missing_confirmation_email(self):
    #     form_data = {
    #         'meeting': 24,
    #         'year': 2015,
    #         'presentation_type': 'Paper',
    #          'title': """<p>A test title with strange characters &part;13C and species names
    #          like <em>Australopithecus afarensis</em></p>""",
    #
    #          'abstract_text': """<p>You think water moves fast? You should see ice. It moves like it has a mind. Like it
    #          knows it killed the world once and got a taste for murder. After the avalanche, it took us a week to climb
    #          out. Now, I don't know exactly when we turned on each other, but I know that seven of us survived the
    #          slide... and only five made it out. Now we took an oath, that I'm breaking now. We said we'd say it was
    #          the snow that killed the other two, but it wasn't. Nature is lethal but it doesn't hold a candle to man.
    #          </p>""",
    #
    #          'acknowledgements': 'I gratefully acknowledge the academy.',
    #          'contact_email': 'denne.reed@gmail.com',
    #          #'confirm_email':  'denne.reed@gmail.com',  # remove email address
    #          'author_set-0-name': 'Denne Reed',
    #          'author_set-0-department': 'Anthropology',
    #          'author_set-0-institution': 'University of Texas at Austin',
    #          'author_set-0-country': 'United States of America',
    #          'author_set-0-email_address': 'denne.reed@gmail.com',
    #     }
    #     response = self.client.post(reverse('meetings:create_abstract'), form_data)
    #     self.assertEqual(response.status_code, 200)  # test that on submit we return the form again
    #     self.assertEqual(response.context_data['form'].errors['confirm_email'][0], u'This field is required.')
    #
    # def test_abstract_with_malformed_confirmation_email(self):
    #     form_data = {
    #         'meeting': 24,
    #         'year': 2015,
    #         'presentation_type': 'Paper',
    #          'title': """<p>A test title with strange characters &part;13C and species names
    #          like <em>Australopithecus afarensis</em></p>""",
    #
    #          'abstract_text': """<p>You think water moves fast? You should see ice. It moves like it has a mind. Like it
    #          knows it killed the world once and got a taste for murder. After the avalanche, it took us a week to climb
    #          out. Now, I don't know exactly when we turned on each other, but I know that seven of us survived the
    #          slide... and only five made it out. Now we took an oath, that I'm breaking now. We said we'd say it was
    #          the snow that killed the other two, but it wasn't. Nature is lethal but it doesn't hold a candle to man.
    #          </p>""",
    #
    #          'acknowledgements': 'I gratefully acknowledge the academy.',
    #          'contact_email': 'denne.reed@gmail.com',
    #          'confirm_email':  'denne.reed',
    #          'author_set-0-name': 'Denne Reed',  # invalid email address
    #          'author_set-0-department': 'Anthropology',
    #          'author_set-0-institution': 'University of Texas at Austin',
    #          'author_set-0-country': 'United States of America',
    #          'author_set-0-email_address': 'denne.reed@gmail.com',
    #     }
    #     response = self.client.post(reverse('meetings:create_abstract'), form_data)
    #     self.assertEqual(response.status_code, 200)  # test that on submit we return the form again
    #     # test that the form contains an appropriate error message
    #     self.assertEqual(response.context_data['form'].errors['confirm_email'][0], u'Enter a valid email address.')
    #
    # def test_abstract_when_contact_email_not_same_as_confirmation_email(self):
    #     form_data = {
    #         'meeting': 24,
    #         'year': 2015,
    #         'presentation_type': 'Paper',
    #          'title': """<p>A test title with strange characters &part;13C and species names
    #          like <em>Australopithecus afarensis</em></p>""",
    #
    #          'abstract_text': """<p>You think water moves fast? You should see ice. It moves like it has a mind. Like it
    #          knows it killed the world once and got a taste for murder. After the avalanche, it took us a week to climb
    #          out. Now, I don't know exactly when we turned on each other, but I know that seven of us survived the
    #          slide... and only five made it out. Now we took an oath, that I'm breaking now. We said we'd say it was
    #          the snow that killed the other two, but it wasn't. Nature is lethal but it doesn't hold a candle to man.
    #          </p>""",
    #
    #          'acknowledgements': 'I gratefully acknowledge the academy.',
    #          'contact_email': 'denne.reed@gmail.com',   # valid email address
    #          'confirm_email':  'reedd@mail.utexas.edu',  # valid email address, but not same as above
    #          'author_set-0-name': 'Denne Reed',
    #          'author_set-0-department': 'Anthropology',
    #          'author_set-0-institution': 'University of Texas at Austin',
    #          'author_set-0-country': 'United States of America',
    #          'author_set-0-email_address': 'denne.reed@gmail.com',
    #     }
    #     response = self.client.post(reverse('meetings:create_abstract'), form_data)
        #self.assertEqual(response.status_code, 200)  # test that on submit we return the form again
        #self.assertEqual(response.context_data['form'].errors['confirm_email'][0],
        #                 u'Contact Email and Confirmation Email must match.')




    #
    # def test_abstract_create_view_get_additioanl_authors(self):
    #     response = self.client.post( reverse('meetings:create_abstract'), {})
    #     self.assertEqual(response.status_code, 200)