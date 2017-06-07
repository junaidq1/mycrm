from django.contrib import admin

# Register your models here.
from .models import Tag

class TagModelAdmin(admin.ModelAdmin):
	list_display = ['tag_name','tag_description','tag_added']
	list_display_links = ['tag_name','tag_description','tag_added']

	search_fields = ['tag_name','tag_description']
	
	
	class Meta:
		model = Tag

admin.site.register(Tag, TagModelAdmin)
