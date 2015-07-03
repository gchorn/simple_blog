from django import forms
from django.contrib.comments.forms import CommentDetailsForm
from django.utils.translation import ungettext, ugettext_lazy as _

class CommentForm(CommentDetailsForm):
	email         = forms.EmailField(label=_("Email address"), required=False)

def get_form():
	return CommentForm
