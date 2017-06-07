
from django.contrib import admin
from .models import Weeklog
# Register your models here.

class WeeklogModelAdmin(admin.ModelAdmin):
	list_display = ['pk','weeknum','week_beginning', 'primary_city_during_week', 'primary_city_weekend', 'notes']
	list_display_links = ['pk','weeknum','week_beginning', 'primary_city_during_week', 'primary_city_weekend', 'notes']
	
	list_filter = ['weeknum','primary_city_during_week', 'primary_city_weekend']
	
	class Meta:
		model = Weeklog

admin.site.register(Weeklog, WeeklogModelAdmin)





