"""mycrm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from master import views as mas 

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', mas.try_to_login, name='login'),
    url(r'^logout/$', mas.try_to_logout, name='logout'),  

    url(r'^$',   mas.go_home, name='user_homepage'),
    url(r'^primary_groups/$', mas.list_of_prim_groups, name='prim_groups'),
    url(r'^primary_group_details/(?P<pk>\d+)/$', mas.prim_group_details, name='prim_group_detail'),   
    url(r'^tag_list/$', mas.show_all_tags, name='tag_list'),
    url(r'^tag_details/(?P<pk>\d+)/$', mas.tag_details, name='tag_detail'),
    #search by city / city deepdive
    url(r'^city_list/$', mas.list_of_cities, name='city_list'),
    #url(r'^city_details/(?P<city>\w+)$', mas.city_deepdive, name='city_detail2'), 
    url(r'^city_details/(?P<city>[\w ]+)$', mas.city_deepdive, name='city_detail2'), 
    #link for contact deepdive      
    url(r'^contact_details/(?P<pk>\d+)/$', mas.indiv_contact_details, name='cont_detail'),
    #edit master details
    url(r'^edit_master/(?P<pk>\d+)/$', mas.edit_master_entry, name='edit_master'),
    url(r'^edit_master_next_date/(?P<pk>\d+)/$', mas.edit_next_contact_in_master, name='edit_master_next_date'),
    url(r'^edit_master_starred/(?P<pk>\d+)/$', mas.edit_starred_in_master, name='edit_master_starred'),
    url(r'^edit_master_prospect/(?P<pk>\d+)/$', mas.edit_prospect_in_master, name='edit_master_prospect'),
    #add a new master entry
    url(r'^add_master/$', mas.add_master_entry, name='add_master'),
    #url(r'^%s/%s/' % (model._meta.app_label, model._meta.model_name), include(model_admin.urls))
    url(r'^add_touchpoint/(?P<pk>\d+)/$', mas.add_contact_touchpoint, name='add_touchpoint'),
    url(r'^edit_touchpoint/(?P<pk>\d+)/(?P<pk2>\d+)/$', mas.edit_contact_touchpoint, name='edit_touchpoint'),
    url(r'^search_contacts/$', mas.search_master_list, name='search_master'),
    #calendar view
    url(r'^forecast_past_due/$', mas.calendar_forecast_past_due, name='cal_view_pastdue'),
    url(r'^forecast/$', mas.calendar_forecast_today, name='cal_view_today'),
    url(r'^forecast_plus1/$', mas.calendar_forecast_plus1, name='cal_view_todayplus1'),
    url(r'^forecast_plus2/$', mas.calendar_forecast_plus2, name='cal_view_todayplus2'),
    url(r'^forecast_beyond/$', mas.calendar_forecast_beyond, name='cal_beyond_that'),
    url(r'^forecast_all/$', mas.calendar_forecast_all, name='cal_all'),
    url(r'^forecast_all_by_imp/$', mas.calendar_forecast_all_by_import, name='cal_all_by_imp'),
   #list of starred folks 
    url(r'^starred/$', mas.list_of_starred, name='list_starred'),
    url(r'^prospects/$', mas.list_of_prospects, name='list_prospects'),
    #dateTimeViewBootstrap3
    #url(r'^example/$', mas.dateTimeViewBootstrap3, name='exp'),
    #url(r'^test/$', mas.testview2, name='test_view'),
]

