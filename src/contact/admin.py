from django.contrib import admin

# Register your models here.
from .models import Contact_log

class Contact_logModelAdmin(admin.ModelAdmin):
	list_display = ['pk', 'contact_name', 'contact_date','contact_type','contact_notes']
	list_display_links = ['pk','contact_name', 'contact_date','contact_type','contact_notes']
	search_fields = ['contact_name', 'contact_date','contact_type']
	list_filter = ['contact_name', 'contact_date','contact_type']
	class Meta:
		model = Contact_log


admin.site.register(Contact_log, Contact_logModelAdmin)
