from django import forms
import datetime
from django.forms.extras.widgets import SelectDateWidget
#from django.contrib.admin.widgets import AdminDateWidget
from django.forms import ModelForm

from .models import Master
from p_groups.models import Group
from tags.models import Tag
from contact.models import Contact_log
from datetimewidget.widgets import DateWidget



class MasterForm(forms.ModelForm):
	class Meta:
		model = Master
		fields = ["first_name", "last_name", "primary_group", "met_where", "notes","city", "prospect", 
		"starred", "email", "phone", "workplace", "title", "ind_imp_rating", "first_met",
		"target_contact_cycle_individual", "dont_update_next_contact_date", "next_contact_date", "tag1"]
		#next_contact_date = forms.DateField(widget=SelectDateWidget)
		widgets = {
			#Use localization and bootstrap 3
			'first_met': DateWidget(usel10n=True, bootstrap_version=3),
			'next_contact_date': DateWidget(usel10n=True, bootstrap_version=3)
		}

class MasterJustNextDateForm(forms.ModelForm):
	class Meta:
		model = Master
		fields = ["next_contact_date"]
		#next_contact_date = forms.DateField(widget=SelectDateWidget)
		# widgets = {
  #           'next_contact_date': SelectDateWidget(attrs={'cols': 30, 'rows': 20}),
  #       }
  		widgets = {
            'next_contact_date': DateWidget(usel10n=True, bootstrap_version=3)
        } 

class MasterJustStarred(forms.ModelForm):
	class Meta:
		model = Master
		fields = ["starred"]

class MasterJustProspect(forms.ModelForm):
	class Meta:
		model = Master
		fields = ["prospect"]


class testForm(forms.Form):
    #date_time = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))
    date = forms.DateField(widget=DateWidget(usel10n=True, bootstrap_version=3))
    #time = forms.TimeField(widget=TimeWidget(usel10n=True, bootstrap_version=3))


		
		