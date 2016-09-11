from django.views import generic
from models import Meeting, Abstract
from django.core.urlresolvers import reverse
from fiber.views import FiberPageMixin
from fiber.models import Page
from forms import AbstractForm, AuthorInlineFormSet
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.mail import send_mail


class MeetingsView(FiberPageMixin, generic.ListView):
    # default template name is 'meetings/meeting_list.html'
    model = Meeting

    def get_fiber_page_url(self):
        return reverse('meetings:meetings')


class MeetingsDetailView(FiberPageMixin, generic.ListView):
    template_name = 'meetings/meeting_detail.html'

    def get_queryset(self):
        # TODO Sort abstracts by lead author last name
        # send a queryset of Authors?
        # convert the queryset object into a list of objects and sort that
        # This needs to be returned in the context not the get_queryset method
        #abstracts = Abstract.objects.select_related().filter(meeting__year__exact=self.kwargs['year'], accepted__exact=True)
        #abstract_list = list(abstracts)
        #abstract_list.sort(key=lambda x: x.author_set.order_by('author_rank')[0].last_name)
        # TODO Add ajax to access absrtact text inline
        return Abstract.objects.select_related().filter(meeting__year__exact=self.kwargs['year'],
                                                        accepted__exact=True).order_by('title')

    # Fetch corresponding fiber page content
    # In this view there is a separate fiber page for
    # every meeting
    def get_fiber_page_url(self):
        return reverse('meetings:meeting_detail', kwargs={'year': self.kwargs['year']})


class AbstractThanksView(FiberPageMixin, generic.ListView):
    template_name = 'meetings/thanks.html'
    model = Abstract

    def get_fiber_page_url(self):
        return reverse('meetings:thanks')


#####################################################################
## First pass at Create Abstract View. Needs Author inline formset ##
#####################################################################
class AbstractCreateView(FiberPageMixin, generic.CreateView):
    template_name = 'meetings/abstract.html'
    model = Abstract
    form_class = AbstractForm
    success_url = '/meetings/abstract/thanks/'

    def get_fiber_page_url(self):
        return reverse('meetings:create_abstract')

    def get(self, request, *args, **kwargs):
        """
        Implementation based on post by Kevin Dias
        http://kevindias.com/writing/django-class-based-views-multiple-inline-formsets/
        Handles GET requests and instantiates blank versions of the form and its inline formsets.
        """

        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        author_formset = AuthorInlineFormSet()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  author_formset=author_formset)  # template expects author_formset in context
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline formsets with
        the passed POST variables and then checking them for validity.
        :param requests:
        :param args:
        :param kwargs:
        :return:
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.meeting_id = 1
        form.year = 2016
        author_formset = AuthorInlineFormSet(self.request.POST)
        if (form.is_valid() and author_formset.is_valid()):
            return self.form_valid(form, author_formset)
        else:
            return self.form_invalid(form, author_formset)

    def form_valid(self, form, author_formset):
        """
        Called if all forms are valid. Creates an Abstract instance along with associated
        Authors and then redirects to a success page.
        :param form:
        :param author_formset:
        :return:
        """
        self.object = form.save()  # save abstract
        author_formset.instance = self.object
        new_authors = author_formset.save(commit=False)
        rank = 1
        for author in new_authors:
            author.author_rank = rank
            author.abstract = self.object
            author.save()
            rank += 1

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, author_formset):
        """
        Called if a form is invalid. Re-renders the form with the context data.
        :param form:
        :param author_form:
        :return:
        """
        #error_message="The form is invalid"
        return self.render_to_response(
            self.get_context_data(form=form,
                                  author_formset=author_formset,
                                  )
        )



#########################################
# Function-based Create Abstract view. ##
#########################################
# TODO Update email addresses in production.


def check_pcode(request):
    if 'pcode' in request.POST and request.POST['pcode'] in ["PR432", "pr432"]:
        return True
    else:
        return False


def create_abstract(request):
    fiber_page = Page.objects.get(url__exact='add')

    # If there is data in the request, i.e. a completed form, then process it
    # otherwise return an empty form
    if request.method == "POST":

        #if there's a request for more author forms add three more inline
        # author forms and reload the page
        if 'add_authors' in request.POST:
            cp = request.POST.copy()  # create a copy of the request

            # the following two lines increase the total forms
            # attribute from the formset manager
            max_forms = cp['author_set-TOTAL_FORMS']
            cp['author_set-TOTAL_FORMS'] = int(max_forms) + 3

            # create new forms from the updated request data
            abstract_form = AbstractForm(cp)
            author_formset = AuthorInlineFormSet(cp)

            # reload the page
            return render(request, 'meetings/add_abstract.html',
                          {
                              'fiber_page': fiber_page,
                          'abstract_form': abstract_form,
                          'author_formset': author_formset,
                          })

        #If submitting the form ...
        abstract = Abstract(year='2016', meeting_id=1)  # set the abstract year
        abstract_form = AbstractForm(request.POST, instance=abstract)  # create a form instance that includes the year

        # validate the abstract information (not authors yet)
        # If abstract info is valid continue to process authors
        # otherwise return form with error message
        if request.POST['contact_email'] != request.POST['validate_email']:
            error_message = 'The contact email does not match the confirmation email. Please try again'
            abstract_form = AbstractForm(request.POST)
            author_formset = AuthorInlineFormSet(request.POST)
            return render(request, 'meetings/add_abstract.html',
                          {
                              'fiber_page': fiber_page,
                          'abstract_form': abstract_form,
                          'author_formset': author_formset,
                          'error_message': error_message,
                          })
        if not check_pcode(request):
            error_message = 'Please verify that you have entered correctly the code displayed at the bottom of the form.'
            abstract_form = AbstractForm(request.POST)
            author_formset = AuthorInlineFormSet(request.POST)
            return render(request, 'meetings/add_abstract.html',
                          {
                              'fiber_page': fiber_page,
                          'abstract_form': abstract_form,
                          'author_formset': author_formset,
                          'error_message': error_message,
                          })

        if abstract_form.is_valid() and request.POST['contact_email'] == request.POST['validate_email'] and check_pcode(
                request):

            # save the abstract form but don't commit to DB till
            # we validate authors
            new_abstract = abstract_form.save(commit=False)
            
            # process author formset
            author_formset = AuthorInlineFormSet(request.POST,
                                                 instance=new_abstract)
            if author_formset.is_valid():

                new_abstract = abstract_form.save()  # save abstract for real
                new_authors = author_formset.save(commit=False)  # need this step to only process completed author forms
                rank = 1
                for author in new_authors:
                    author.author_rank = rank
                    author.abstract = new_abstract
                    author.save()
                    rank += 1
                author_names = []
                for author in new_authors:
                    author_names.append(author.name)

                # send validation email
                message = """Thank you for submitting your abstract entitled %s.The review process will
                begin December 3 and we expect to notify you prior to the end of January.If you have any
                questions prior to then, you can contact John Yellen at jyellen@nsf.gov \n \n The
                Paleoanthropology Society" % new_abstract.title"""

                #send_mail('Paleoanthropology Abstract Submission',  # subject
                #          message, # message text
                #          'webmaster@paleoanthro.org',  # from
                #          [request.POST['contact_email']],  # to
                #          fail_silently=False)  # options

                # TODO Send validation email
                # email a copy of the abstract to John Yellen and Deborah O
                #
                #abstract_message = "Presentation Type: %s \n Title: %s \n Authors: %s \n Abstact: %s \n Acknowledgements: %s \n References: %s \n Funding %s \n Comments: %s \n Contact Email: %s \n " % (new_abstract.presentation_type, new_abstract.title, "; ".join(author_names), new_abstract.abstract_text, new_abstract.acknowledgements, new_abstract.references, new_abstract.funding, new_abstract.comments, new_abstract.contact_email)
                #send_mail('Paleoanthropology Abstract Submission',
                #          abstract_message, 'paleoanthro@paleoanthro.org',  # from
                #          ['jyellen@nsf.gov', 'deboraho@sas.upenn.edu']   # to
                #)

                # redirect to confirmation page
                return render(request, 'meetings/abstract_confirmation.html',
                              {
                                  'fiber_page': fiber_page,
                                  'abstract': new_abstract,
                                  'authors': new_authors})
                #return HttpResponseRedirect('/abstract/confirmation/',{'abstract':abstract})

            else: # reload the page with an error message
                error_message = 'There was an error with the author portion of the form. Please try again'
                abstract_form = AbstractForm(request.POST)
                author_formset = AuthorInlineFormSet(request.POST)
                return render(request, 'meetings/add_abstract.html',
                              {
                                  'fiber_page': fiber_page,
                              'abstract_form': abstract_form,
                              'author_formset': author_formset,
                              'error_message': error_message,
                              })

        else:
            error_message = 'There was an error with the form. Please try again'
            abstract_form = AbstractForm(request.POST)
            author_formset = AuthorInlineFormSet(request.POST)

            return render(request, 'meetings/add_abstract.html',
                          {
                              'fiber_page': fiber_page,
                          'abstract_form': abstract_form,
                          'author_formset': author_formset,
                          'error_message': error_message,
                          })

    else:   # if there's no data open a blank form...
        # data for form testing
        abstract_testdata = {
        'contact_email': 'denne.reed@gmail.com',
        'validate_email': 'denne.reed@gmail.com',
        'title': 'Test title',
        'abstract_text': 'Text abstract text',
        'acknowledgements': 'Test acknowledgements',
        'presentation_type': 'Poster',
        }
        abstract_form = AbstractForm()
        author_formset = AuthorInlineFormSet()
        return render(request, 'meetings/add_abstract.html',
                      {
                          'fiber_page': fiber_page,
                          'abstract_form': abstract_form,
                          'author_formset': author_formset,
                      })