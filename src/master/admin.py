from django.contrib import admin

# Register your models here.
from .models import Master, Importance

class MasterModelAdmin(admin.ModelAdmin):
	list_display = ['pk','first_name', 'last_name','primary_group',  'starred','prospect','city', 'ind_imp_rating', 'first_met', 'next_contact_date','target_contact_cycle_individual','dont_update_next_contact_date','met_where', 'added']
	list_display_links = [	'pk','first_name', 'last_name','primary_group', 'starred','prospect','city',  'ind_imp_rating', 'first_met', 'next_contact_date','target_contact_cycle_individual','dont_update_next_contact_date','met_where', 'added']
	search_fields = ['primary_group',  'city', 'ind_imp_rating']
	list_filter = ['primary_group',  'city', 'ind_imp_rating', 'starred']
	class Meta:
		model = Master

class ImportanceModelAdmin(admin.ModelAdmin):
	list_display = ['pk', 'importance_descrip', 'importance_ranking']
	list_display_links = ['pk', 'importance_descrip', 'importance_ranking']
	class Meta:
		model = Importance

admin.site.register(Master, MasterModelAdmin)
admin.site.register(Importance, ImportanceModelAdmin)
