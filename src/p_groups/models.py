from __future__ import unicode_literals

from django.db import models
#from master.models import Importance

# Create your models here.
class Group(models.Model):
	group_name = models.CharField(max_length=125)
	group_description = models.TextField(max_length=300, null=True)
	IMP_RATING_CHOICES = (
	    ('v high', 'v high'),
	    ('high', 'high'),
	    ('medium', 'medium'),
	    ('low', 'low'),
	)
	group_imp_rating =  models.CharField(max_length=24, choices=IMP_RATING_CHOICES)
	group_strategy = models.TextField(max_length=500, null=True)
	target_contact_cycle_weeks = models.IntegerField(null=False, blank=False)

	def __unicode__(self):
		return self.group_name

	def __string__(self):
		return self.group_name 

	# def get_absolute_url(self):
	# 	return reverse("prim_group_detail", kwargs={"pk": self.pk} )