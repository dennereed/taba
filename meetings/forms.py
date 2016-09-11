from django.forms import ModelForm
from models import Abstract, Author, Meeting
from django.forms.models import inlineformset_factory
from django.forms.widgets import Textarea, TextInput, HiddenInput
from django import forms
from captcha.fields import CaptchaField


# Abstract Model Form
class AbstractForm(ModelForm):
    confirm_email = forms.EmailField(widget=TextInput(attrs={'size': 60}))
    meeting = forms.ModelChoiceField(queryset=Meeting.objects.filter(year__exact=2016), empty_label=None)
    year = forms.IntegerField(widget=HiddenInput, initial=2016)
    #human_test = CaptchaField(help_text='Enter the solution')

    class Meta:
        model = Abstract
        fields = (
            'year',
            'meeting',
            'presentation_type',
            'title',
            'abstract_text',
            'acknowledgements',
            'references',
            'comments',
            'contact_email',
            'confirm_email',
        )

        widgets = {
            'contact_email': TextInput(attrs={'size': 60, }),

            'title': Textarea(attrs={'cols': 60, 'rows': 2}),
            'abstract_text': Textarea(attrs={'cols': 60, 'rows': 20}),
            'acknowledgements': Textarea(attrs={'cols': 60, 'rows': 5}),
            'references': Textarea(attrs={'cols': 60, 'rows': 5}),
            'comments': Textarea(attrs={'cols': 60, 'rows': 10}),
        }


# Author Model Form
class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = (
            'abstract',
            'author_rank', 'last_name', 'first_name', 'name', 'department',  'institution',
            'country', 'email_address',
        )

# generate an inline formset for authors, exclude author rank field,
# which the view will add automatically. Show three blank author forms
# and don't show delete buttons
AuthorInlineFormSet = inlineformset_factory(Abstract, Author,
                                            form=AuthorForm,
                                            extra=3,
                                            exclude=('author_rank',),
                                            can_delete=False,
                                            )

