from django.contrib import admin
from models import *
from django import forms
from django.forms.widgets import Textarea
from django.http import HttpResponse
from django.template import loader, Context
import unicodecsv


###########################
# Abstract Report Actions #
###########################

def create_abstract_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="taba_abstracts.csv"'
    writer = unicodecsv.writer(response)
    writer.writerow(['id', 'contact_email', 'presentation_type', 'title', 'abstract_text', 'acknowledgements',
                     'references', 'comments', 'year', 'abstract_rank', 'authors'])

    for abstract in queryset.all():
        author_list = []
        for a in abstract.author_set.all().order_by('author_rank'):
            author_list.append(a.name)
        writer.writerow(
            [abstract.id, abstract.contact_email, abstract.presentation_type, abstract.title, abstract.abstract_text,
             abstract.acknowledgements, abstract.references, abstract.comments, abstract.year,
             abstract.abstract_rank, ', '.join(author_list)]
        )

    return response
create_abstract_csv.short_description = "Download .csv"


# def create_abstract4meeting_html(modeladmin, request, queryset):
#     abstracts=queryset
#     for abstract in abstracts:
#         abstract.authors = abstract.author_set.all().order_by("author_rank")
#         if len(abstract.authors) > 2:
#             try:
#                 abstract.authors = abstract.authors[0].name.split()[-1]+" et al."  # get the last name
#             except IndexError:
#                 abstract.authors = abstract.authors[0].name.split()[0]+" et al."
#         if len(abstract.authors) == 2:
#             try:
#                 abstract.authors = abstract.authors[0].name.split()[-1]+" and "+abstract.authors[1].name.split()[-1]
#             except IndexError:
#                 abstract.authors = abstract.authors[0].name.split()[0]+" and "+abstract.authors[1].name.split()[0]
#         if len(abstract.authors) == 1:
#             try:
#                 abstract.authors = abstract.authors[0].name.split()[-1]  # get the last name
#             except IndexError:
#                 abstract.authors = abstract.authors[0].name.split()[0]  # get the last name
#
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="PaleoAnthro_abstracts_for_meeting.html"'
#     t=loader.get_template("meetings/abstract_meeting_template.html")
#     c=Context({
#         'data': abstracts,
#     })
#     response.write(t.render(c))
#     return response
# create_abstract4meeting_html.short_description = "Download .html for meeting"

def create_abstract4meeting_html(modeladmin, request, queryset):
    abstracts = queryset.order_by('abstract_rank')
    for abstract in abstracts:
        abstract.authors = abstract.author_set.all().order_by("author_rank")
        # if len(abstract.authors) > 2:
        #     try:
        #         abstract.authors = abstract.authors[0].name.split()[-1]+" et al."  # get the last name
        #     except IndexError:
        #         abstract.authors = abstract.authors[0].name.split()[0]+" et al."
        # if len(abstract.authors) == 2:
        #     try:
        #         abstract.authors = abstract.authors[0].name.split()[-1]+" and "+abstract.authors[1].name.split()[-1]
        #     except IndexError:
        #         abstract.authors = abstract.authors[0].name.split()[0]+" and "+abstract.authors[1].name.split()[0]
        # if len(abstract.authors) == 1:
        #     try:
        #         abstract.authors = abstract.authors[0].name.split()[-1]  # get the last name
        #     except IndexError:
        #         abstract.authors = abstract.authors[0].name.split()[0]  # get the last name

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="PaleoAnthro_abstracts_for_meeting.html"'
    t = loader.get_template("meetings/abstract_meeting_template.html")
    c = Context({
        'data': abstracts,
    })
    response.write(t.render(c))
    return response
create_abstract4meeting_html.short_description = "Download .html for meeting"


#################
# Admin Classes #
#################

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email_address', 'abstract', 'author_rank',)
    list_display_links = ['id', 'name']
    list_filter = ['abstract']
    search_fields = ['id', 'name', 'email_address', 'abstract']


class AuthorInline(admin.TabularInline):
    model = Author


class AbstractAdminForm(forms.ModelForm):
    class Meta:
        model = Abstract
        #widgets = {'title': TextInput(attrs={'size': 120, })}
        widgets = {'title': Textarea(attrs={'cols': 80, 'rows': 2})}
        exclude = ()


class AbstractAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_email', 'presentation_type', 'title', 'year', 'abstract_rank', 'accepted')
    list_display_links = ['id', 'title']
    list_editable = ['accepted', 'abstract_rank']
    list_filter = ['year', 'presentation_type', 'accepted']
    search_fields = ['title', 'author__name']
    form = AbstractAdminForm
    inlines = [AuthorInline, ]
    actions = [create_abstract_csv, create_abstract4meeting_html]


class AbstractInline(admin.TabularInline):
    model = Abstract


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'year', 'location', 'start_date', 'end_date', 'associated_with')
    list_display_links = ['id', 'location']
    list_editable = []
    list_filter = ['associated_with']
    search_fields = ['location', 'associated_with', 'description']
    inlines = [AbstractInline, ]

admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Abstract, AbstractAdmin)
admin.site.register(Author, AuthorAdmin)

