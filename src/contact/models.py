from __future__ import unicode_literals

from django.db import models
#from django.utils import timezone
from master.models import Master
from p_groups.models import Group
import datetime
from django.db.models.signals import post_save
from django.db.models import Count, Sum, Avg, Max
from django.core.urlresolvers import reverse

# Create your models here.


class Contact_log(models.Model):
	contact_name = models.ForeignKey('master.Master')
	contact_date = models.DateField(auto_now=False, auto_now_add=False, default = datetime.date.today)
	#contact_date = models.DateField(auto_now=False, auto_now_add=False, default = django.utils.timezone.now)
	CONTACT_TYPE_CHOICES = (
		('in_person', 'in_person'),
		('email', 'email'),
		('text', 'text'),
		('phone', 'phone'),
		('socialmedia', 'socialmedia'),
		('other', 'other'),
	)
	contact_type =  models.CharField(max_length=12, choices=CONTACT_TYPE_CHOICES, null=False, blank=False)
	contact_notes = models.TextField(max_length=2500, null=True, blank=True)
	#next_contact_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True) 

	# def __unicode__(self):
	# 	return self.contact_name 

	def __string__(self):
		return self.contact_name

	def get_absolute_url(self):
		return reverse("cont_detail", kwargs={"pk": self.contact_name_id})  
 
	


#this is signal receiver that updates the 'next target meet date' after a contact log entry
def update_next_meet_date(sender, instance, **kwargs):
	#check if not update ISNT flagged. Only then update the meet date
	dont_update_flag = Master.objects.filter(contact_log__contact_name=instance.contact_name)[0].dont_update_next_contact_date	
	if not dont_update_flag:  #i.e. if don't update flag isn't selected, then
		#estimate target contact cycle at the individual level
		ind_tar_weeks = Master.objects.filter(contact_log__contact_name=instance.contact_name)[0].target_contact_cycle_individual	
		
		#estimate target contact cycle for the entire group
		m = Master.objects.filter(contact_log__contact_name=instance.contact_name)[0]
		grp_tar_weeks = Group.objects.filter(group_name = m.primary_group)[0].target_contact_cycle_weeks

		#final days to meet calc - if the individual contact days value exists use that, else use the group cycle
		if ind_tar_weeks > 0 :
			meet_days = ind_tar_weeks * 7
		else:
			meet_days = grp_tar_weeks * 7

		touchpoints = Contact_log.objects.filter(contact_name_id = m.id) #total contacts in history
		touchpoints = touchpoints.aggregate(Max('contact_date'))
		date_most_recently_met = touchpoints.values()[0]

		Master.objects.filter(contact_log__contact_name=instance.contact_name).update(next_contact_date=date_most_recently_met + datetime.timedelta(days= meet_days))

#this is a post save signal generator once a new contact log entry is made
post_save.connect(update_next_meet_date, sender=Contact_log)


	


# this is the signal receiver that creates a new Contact log item after master entry is created
def create_a_contact_after_master_entry(sender, instance, **kwargs):
	c = Contact_log.objects.filter(contact_name_id = instance.id)
	#only create a new contact instance if an existing one doesnt exist (i.e. dont create new for master updates)
	#not c checks for an empty dict
	if not c: #if there is no prior record of meeting this person, i.e. not an update)
		if instance.first_met is not None : #if first met date is present in master record,specify that date in the contact log
			Contact_log.objects.create(contact_name=instance, contact_date=instance.first_met, contact_type='in_person', contact_notes='first contact')
		else: #if no record of meeting date, use the default (today)
			Contact_log.objects.create(contact_name=instance, contact_type='in_person', contact_notes='first contact')
	#Contact_log.objects.create(contact_name=instance, contact_date=instance.first_met, contact_type='in-person', contact_notes='first contact')


#this is a post save signal generator once a new master entry is made
post_save.connect(create_a_contact_after_master_entry, sender=Master)


