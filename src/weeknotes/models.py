from __future__ import unicode_literals
import datetime
from django.db import models
from django.db.models.signals import post_save

# Create your models here.
 

 
class Weeklog(models.Model):
	year = models.IntegerField(null=True, blank=True)
	weeknum = models.IntegerField(null=True, blank=True) 
	week_beginning = models.DateField(auto_now=False, auto_now_add=False) 
	primary_city_during_week = models.CharField(max_length=150)
	primary_city_weekend = models.CharField(max_length=150)
	notes = models.TextField(max_length=2000, null=True, blank=True)
	
	@property
	def year_week(self):
		return ''.join([self.year, '_', self.weeknum])

	def __unicode__(self):
		return self.notes

	def __string__(self):
		return self.notes


# this is the signal receiver to create a weeknum and year from the date
def create_a_weeknum(sender, instance, **kwargs):
	w = Weeklog.objects.get(id = instance.id)
	
	yr = w.week_beginning.isocalendar()[0]
	wknm = w.week_beginning.isocalendar()[1]
	Weeklog.objects.filter(id = instance.id).update(weeknum=wknm, year=yr)

#this is a post save signal generator once a week entry is made
post_save.connect(create_a_weeknum, sender=Weeklog)
