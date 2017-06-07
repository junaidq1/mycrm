from __future__ import unicode_literals
from django.db import models
import datetime
from django.utils import timezone
from django.core.urlresolvers import reverse
from p_groups.models import Group

#from contact.models import Contact_log
from tags.models import Tag
from django.db.models.signals import post_save


# Create your models here.

class Master(models.Model):
	first_name = models.CharField(max_length=120)
	last_name = models.CharField(max_length=120)
	met_where = models.CharField(max_length=500, null=True, blank=True)
	notes = models.TextField(max_length=2500, null=True, blank=True)
	city = models.CharField(max_length=120, null=False, blank=False, default='unknown')
	prospect = models.BooleanField(default=False)
	starred = models.BooleanField(default=False)
	email = models.CharField(max_length=120, null=True, blank=True)
	phone = models.CharField(max_length=120, null=True, blank=True)
	workplace = models.CharField(max_length=120, null=True, blank=True)
	title = models.CharField(max_length=120, null=True, blank=True)
	#
	primary_group = models.ForeignKey('p_groups.Group') 
	IMP_RATING_CHOICES = (
	    ('v high', 'v high'),
	    ('high', 'high'),
	    ('medium', 'medium'),
	    ('low', 'low'),
	)
	ind_imp_rating =  models.CharField(max_length=24, choices=IMP_RATING_CHOICES, null=True, blank=True)
	first_met = models.DateField(auto_now=False, auto_now_add=False, default = datetime.date.today, null=True, blank=True)
	added = models.DateTimeField(auto_now=True, auto_now_add=False)
	target_contact_cycle_individual = models.IntegerField(null=True, blank=True)
	dont_update_next_contact_date = models.BooleanField(default=False)
	next_contact_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True) 
	tag1 = models.ManyToManyField(Tag, blank=True)

	@property
	def full_name(self):
		return ''.join([self.first_name, '_', self.last_name])

	def __unicode__(self):
		return self.full_name

	def __string__(self):
		return self.full_name

	def get_absolute_url(self):
		return reverse("cont_detail", kwargs={"pk": self.pk} )

	def go_to_forecast(self):
		return reverse("cal_view_today")

	def go_to_starred(self):
		return reverse("list_starred")	

	def go_to_prospects(self):
		return reverse("list_prospects")	

	# def url2(self):
	# 	return reverse( url(r'^admin/master/26/change/'))	

class Importance(models.Model):
	importance_descrip = models.CharField(max_length=30)
	importance_ranking = models.IntegerField()

	def __unicode__(self):
		return self.importance_descrip

	def __string__(self):
		return self.importance_descrip



