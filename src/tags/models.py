from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Tag(models.Model):
	tag_name = models.CharField(max_length=150)
	tag_description = models.TextField(max_length=2000, null=True, blank=True)
	tag_added = models.DateTimeField(auto_now=False, auto_now_add=True)
	
	def __unicode__(self):
		return self.tag_name

	def __string__(self):
		return self.tag_name