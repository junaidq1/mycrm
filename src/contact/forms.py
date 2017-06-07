from django import forms
import datetime
from django.forms.extras.widgets import SelectDateWidget
#from django.contrib.admin.widgets import AdminDateWidget
from django.forms import ModelForm

from .models import Contact_log
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget



class ContactForm(forms.ModelForm):
	class Meta:
		model = Contact_log
		fields = ["contact_date", "contact_type", "contact_notes"] 
		widgets = {
            'contact_date': DateWidget(usel10n=True, bootstrap_version=3)
        } 
		# widgets = {
  #           'next_contact_date': SelectDateWidget(attrs={'cols': 30, 'rows': 20}),
  #       }
  		

class EditContactForm(forms.ModelForm):
	class Meta:
		model = Contact_log
		fields = ["contact_name", "contact_date", "contact_type", "contact_notes"] 