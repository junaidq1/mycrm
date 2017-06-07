from django.contrib import admin

# Register your models here.
from .models import Group

class GroupModelAdmin(admin.ModelAdmin):
	list_display = ['pk','group_name','group_description','group_imp_rating','group_strategy','target_contact_cycle_weeks']
	list_display_links = ['pk','group_name','group_description','group_imp_rating','group_strategy','target_contact_cycle_weeks']

	search_fields = ['pk','group_name','group_imp_rating','target_contact_cycle_weeks']
	list_filter = ['group_name','group_imp_rating','target_contact_cycle_weeks']
	class Meta:
		model = Group


admin.site.register(Group, GroupModelAdmin)
