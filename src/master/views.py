from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import connection  #for custom SQL
from django.db.models import Count, Sum, Avg, Max, Min,Q
from .forms import MasterForm, MasterJustNextDateForm, MasterJustStarred, MasterJustProspect, testForm
from contact.forms import ContactForm, EditContactForm
import datetime
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login, logout
#from django_tables2 import RequestConfig  #django tables
#from .tables import MasterTable #django tables

from .models import Master, Importance
from p_groups.models import Group
from tags.models import Tag
from contact.models import Contact_log
# Create your views here.


#login on navbar
def try_to_login(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		login(request, user)
		return HttpResponseRedirect( '/' )
	else:
		return HttpResponseRedirect( '/' )

def try_to_logout(request):
	logout(request)
	return HttpResponseRedirect( '/' )


def go_home(request):	
	return render(request, "home.html", {})


# this helper function below is a custom func to convert the cursor object return to a dict
def dictfetchall(cursor):
	#Return all rows from a cursor as a dict
	columns = [col[0] for col in cursor.description]
	return [
		dict(zip(columns, row))
		for row in cursor.fetchall()
	]

#search for contacts by name
@login_required
def search_master_list(request):
	#queryset_list = Employee.objects.all()   #add active filter here
	queryset_list = Master.objects.all()
	query = request.GET.get("q1")
	if query:  
		queryset_list = queryset_list.filter(
						Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(workplace__icontains=query)
						)
		#print queryset_list
	num_contacts = len(queryset_list)	
	context = {
	"queryset_list":queryset_list,
	"query": query,
	"num_contacts": num_contacts
	}
	return render(request, "search_master_list.html", context)


#get the list of primary groups
@login_required
def list_of_prim_groups(request):
	#try this istead of raw sql
	cursor = connection.cursor()

	#this is one beast of a query given all that is does (mainly calculating variance from avg. at contact level and rolling up to group)
	cursor.execute(
	'''SELECT P.id AS group_id, P.group_name, P.number_of_members, P.group_imp_rating, P.target_contact_cycle_weeks,
	  importance_ranking,
	  ROUND(AVG(f_target_cycle),1) as avg_target_weeks,
	  ROUND(AVG(avg_weeks), 1) as avg_actuals_weeks,
	  ROUND((( AVG(avg_weeks) / AVG(f_target_cycle)) -1)*100, 1) AS delta_perc
	FROM
	(SELECT contact_name_id, primary_group_id, first_name, last_name, group_name, group_imp_rating,
	  B.target_contact_cycle_individual AS ind_target_cycle,
	  C.target_contact_cycle_weeks AS group_target_cycle,
	  COUNT(contact_date) AS tot_meets, MIN(contact_date) AS first,
	  (current_date - MIN(contact_date)) AS act_days,
	  (current_date - MIN(contact_date)) / 7.0 AS act_weeks,
	  ROUND(((current_date - MIN(contact_date)) / (7.0 * COUNT(contact_date))),1) AS avg_weeks,
	  CASE WHEN B.target_contact_cycle_individual IS NOT NULL THEN B.target_contact_cycle_individual ELSE C.target_contact_cycle_weeks END AS F_target_cycle
	FROM contact_contact_log AS A
	INNER JOIN master_master AS B ON A.contact_name_id = B.id
	INNER JOIN p_groups_group AS C ON B.primary_group_id = C.id
	WHERE contact_date > now() - interval '1 year' AND dont_update_next_contact_date = FALSE
	GROUP BY contact_name_id, primary_group_id, first_name, last_name, group_name, group_imp_rating,
	  B.target_contact_cycle_individual,C.target_contact_cycle_weeks) AS s_query
	FULL JOIN (SELECT PG.id, PG.group_name, PG.group_imp_rating, PG.target_contact_cycle_weeks,
		COUNT(A.primary_group_id) AS number_of_members
		FROM master_master AS A
		INNER JOIN p_groups_group AS PG ON PG.id = A.primary_group_id
		GROUP BY PG.id, PG.group_name, PG.group_imp_rating, PG.target_contact_cycle_weeks
		ORDER BY PG.id) as P ON s_query.primary_group_id = P.id
	INNER JOIN master_importance AS I ON P.group_imp_rating = I.importance_descrip
	GROUP BY group_id, P.group_name, P.number_of_members, P.group_imp_rating, 
		P.target_contact_cycle_weeks, importance_ranking
	ORDER BY importance_ranking, delta_perc DESC;''', [])

	#recent_reviews1 = cursor.fetchall()
	prim_groups = dictfetchall(cursor)
	group_count = len(prim_groups)
	total_contacts = len(Master.objects.all())
	context = {
	"username": request.user,  #update this
	"group_list": prim_groups,
	"group_count": group_count,
	"total_contacts":total_contacts,
	} 
	return render(request, "list_of_primary_groups.html", context)


#get the list of locations (cities for contacts)
@login_required
def list_of_cities(request):
	#try this istead of raw sql
	cursor = connection.cursor()

	cursor.execute(
	'''SELECT city, count(*) AS num_by_city
	FROM master_master
	GROUP BY city
	ORDER BY num_by_city DESC''', [])

	list_of_cities = dictfetchall(cursor)
	city_count = len(list_of_cities)	
	context = {
	"list_of_cities": list_of_cities,
	"city_count": city_count,
	} 
	return render(request, "list_of_cities.html", context)

#city deepdive (link from above)
@login_required
def city_deepdive(request, city):
	
	#city_contacts = Master.objects.filter(city=city) 

	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS contact_id,
		group_name,
		A.id AS master_id,
		first_name,
		last_name,
		city,
		prospect,
		starred, 
		contact_date AS last_contact,	
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS target_next_contact_date,
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
	WHERE city = %s
	ORDER BY starred DESC, days_to_next_contact, contact_date DESC''', [city])

	city_contacts = dictfetchall(cursor)
	city_count = len(city_contacts)
	context = {
	"city":city,
	"city_contacts": city_contacts,
	"city_count": city_count,
	} 
	return render(request, "city_deepdive.html", context)



#details for a single primary group when you click on it
@login_required
def prim_group_details(request, pk=None):
	custom_grp_id = pk
	grp = Group.objects.get(pk=pk)

	cursor = connection.cursor()
	#CAST(round(julianday('now') - julianday(contact_date), 0) AS INT)  AS days_since_last_contact,
	#CAST(round(julianday(next_contact_date) - julianday('now'), 0) AS INT)  AS days_to_next_contact,
	#DATE_PART('day', now() - contact_date) AS days_since_last_contact,
	#DATE_PART('day', next_contact_date - now() ) AS days_to_next_contact,
	#DATE_PART('day', DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,

	#yes this query is a beast -- it calculates variance from avg.
	cursor.execute(
	'''SELECT *, 
	CASE WHEN avg_weeks > 0 THEN ROUND(((avg_weeks/f_target_cycle) -1)*100, 1) ELSE NULL END AS delta_perc
	FROM
	(SELECT B.id, first_name, last_name, group_name, B.primary_group_id, city, prospect, starred,dont_update_next_contact_date,
	  CASE WHEN B.ind_imp_rating IS NOT NULL THEN B.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
	  B.target_contact_cycle_individual AS ind_target_cycle,
	  C.target_contact_cycle_weeks AS group_target_cycle,
	  X.l_contact_date AS last_contact,
	  (DATE(now() - 8 * interval '1 hour') - X.l_contact_date) AS days_since_last_contact,
	  next_contact_date AS target_next_contact_date,
	  (next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,	
	  COUNT(contact_date) AS tot_meets, 
	  MIN(contact_date) AS first,
	  (current_date - MIN(contact_date)) AS act_days,
	  (current_date - MIN(contact_date)) / 7.0 AS act_weeks,
	  CASE WHEN dont_update_next_contact_date = FALSE THEN ROUND(((current_date - MIN(contact_date)) / (7.0 * COUNT(contact_date))),1)
	  	 ELSE 0 END AS avg_weeks,
	  CASE WHEN B.target_contact_cycle_individual IS NOT NULL THEN B.target_contact_cycle_individual 
	     ELSE C.target_contact_cycle_weeks END AS F_target_cycle
	FROM master_master AS B
	LEFT JOIN (SELECT * FROM contact_contact_log WHERE contact_date > now() - interval '1 year') AS A 
		ON B.id = A.contact_name_id
	INNER JOIN p_groups_group AS C ON B.primary_group_id = C.id
	LEFT JOIN (SELECT  contact_name_id,
		MAX(contact_date) AS l_contact_date, --last contact date
		COUNT(contact_date) AS num_contacts --number of contacts
		FROM contact_contact_log
		WHERE contact_date > now() - interval '1 year'
		GROUP BY contact_name_id) AS X ON B.id = X.contact_name_id 
	GROUP BY B.id, first_name, last_name, group_name, primary_group_id, city, prospect, starred,dont_update_next_contact_date,
	  B.target_contact_cycle_individual,C.target_contact_cycle_weeks, X.l_contact_date, next_contact_date,
	  (next_contact_date - DATE(now() - 8 * interval '1 hour')),
	  (CASE WHEN B.ind_imp_rating IS NOT NULL THEN B.ind_imp_rating ELSE C.group_imp_rating END) ) AS S1
	WHERE primary_group_id = %s
	ORDER BY delta_perc DESC;''', [custom_grp_id])

	#recent_reviews1 = cursor.fetchall() 
	group_details = dictfetchall(cursor)

	context = {
	"username": request.user,  #update this
	"group_details": group_details,
	"grp": grp,
	
	}  
	return render(request, "primary_group_details.html", context)


#show all tags
@login_required
def show_all_tags(request):	
	#get a list of all unique tags and the count of master entries for each
	tag_set = Tag.objects.all().annotate(num_masters = Count('master')).order_by('-num_masters')
	context = {
	"username": request.user,  #update this
	"tag_set": tag_set,
	} 
	return render(request, "list_of_tags_and_counts.html", context)



#show details for each tag
@login_required
def tag_details(request, pk=None):
	tag_id = pk
	tg = Tag.objects.get(pk=pk)
	
	#CAST(round(julianday('now') - julianday(contact_date), 0) AS INT)  AS days_since_last_contact,
	#CAST(round(julianday(next_contact_date) - julianday('now'), 0) AS INT)  AS days_to_next_contact,
	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
			A.id AS contact_id,
			group_name,
			A.id AS master_id,
			first_name,
			last_name,
			CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
			city,
			starred,
			prospect, 
			importance_ranking,
			contact_date AS last_contact,
			(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
			(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
			next_contact_date AS target_next_contact_date,
	num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	INNER JOIN  p_groups_group AS C ON A.primary_group_id = C.id
	INNER JOIN  master_master_tag1 AS D ON A.id = D.master_id
	INNER JOIN master_importance AS E ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = E.importance_descrip
	WHERE D.tag_id = %s
	ORDER BY importance_ranking, days_to_next_contact, group_name, contact_date DESC''', [tag_id])

	tag_details = dictfetchall(cursor)
	context = {
	"username": request.user,  #update this
	"tag_details": tag_details,
	"tg": tg,
	
	} 
	return render(request, "tag_deepdive.html", context)


# deepdive into contact history with a single individual contact (SUPER IMPORTANT)
@login_required
def indiv_contact_details(request, pk=None):
	#tag_id = pk
	name = get_object_or_404(Master, pk=pk)  #Master object
	pg = Group.objects.get(id = name.primary_group_id)  #primary group of object
	total_touchpoints = Contact_log.objects.filter(contact_name_id = name.id) #total contacts in history
	total_touchpoints_count = len(total_touchpoints)
	#total contact touchpoints in the last year
	last_year_touchpoints = total_touchpoints.filter(contact_date__gte = (datetime.date.today() - datetime.timedelta(days= 365))).order_by("-contact_date")
	last_year_touchpoints_count = len(last_year_touchpoints)
	#last meeting date 
	most_recently_met = total_touchpoints.aggregate(Max('contact_date'))
	most_recently_met = most_recently_met.values()[0]
	most_recent_met_medium = Contact_log.objects.filter(contact_name_id = name.id).order_by("-contact_date")[0].contact_type

	most_recently_met_inperson = Contact_log.objects.filter(contact_name_id = name.id).filter(contact_type='in_person').aggregate(Max('contact_date'))
	most_recently_met_inperson = most_recently_met_inperson.values()[0]
	#farthest away meeting in the last year
	earliest_in_last_year = last_year_touchpoints.aggregate(Min('contact_date'))
	earliest_in_last_year = earliest_in_last_year.values()[0]
	#the value below is in days (not date)
	if last_year_touchpoints_count >= 1:
		avg_time_between_meets_last_yr =  ((datetime.date.today() - earliest_in_last_year).days) / float(last_year_touchpoints_count)
		avg_time_between_meets_last_yr_weeks = avg_time_between_meets_last_yr / 7
	else:
		avg_time_between_meets_last_yr = 'NA'
		avg_time_between_meets_last_yr_weeks = 'NA'
	
	if name.next_contact_date is not None:
		days_to_next_meeting = ( name.next_contact_date - datetime.date.today()).days
	else:
		days_to_next_meeting = 'Not specified'

	tags_added = name.tag1.all()

	context = {
	"username": request.user,  #update this
	"name": name,
	"pg": pg,
	"total_touchpoints": total_touchpoints,
	"total_touchpoints_count": total_touchpoints_count,
	"last_year_touchpoints": last_year_touchpoints,
	"last_year_touchpoints_count": last_year_touchpoints_count,
	"most_recently_met": most_recently_met,
	"most_recent_met_medium": most_recent_met_medium,
	"most_recently_met_inperson": most_recently_met_inperson,
	"earliest_in_last_year": earliest_in_last_year,
	"avg_time_between_meets_last_yr": avg_time_between_meets_last_yr,
	"avg_time_between_meets_last_yr_weeks": avg_time_between_meets_last_yr_weeks,
	"days_to_next_meeting": days_to_next_meeting,	
	"tags_added": tags_added,
	} 
	return render(request, "contact_log_details.html", context)


# edit an existing master contact
@login_required
def edit_master_entry(request, pk=None):
	mas = get_object_or_404(Master, pk=pk)
	form = MasterForm(request.POST or None, request.FILES or None, instance=mas)
	if form.is_valid():
		try:
			instance = form.save(commit=False)
			#instance.master = Master.objects.get(pk=pk)
			instance.save()
			form.save_m2m() # this is essential - it saves the manytomany
			return HttpResponseRedirect( instance.get_absolute_url() )
		except:
			return HttpResponseRedirect('/contact_details/%s' %(pk))
	context = {
		"form": form,
		"mas": mas,
	}
	return render(request, "edit_master.html", context)


# edit just the next contact date for an existing master contact
@login_required
def edit_next_contact_in_master(request, pk=None):
	mas = get_object_or_404(Master, pk=pk)
	form = MasterJustNextDateForm(request.POST or None, request.FILES or None, instance=mas)
	if form.is_valid():
		try:
			instance = form.save(commit=False)
			#instance.master = Master.objects.get(pk=pk)
			instance.save()
			return HttpResponseRedirect( instance.go_to_forecast() )
		except:
			return HttpResponseRedirect('/')
	context = {
		"form": form,
		"mas": mas,
	}
	return render(request, "edit_master_next_date_only.html", context)

# edit just the starred status for an existing master contact
@login_required
def edit_starred_in_master(request, pk=None):
	mas = get_object_or_404(Master, pk=pk)
	form = MasterJustStarred(request.POST or None, request.FILES or None, instance=mas)
	if form.is_valid():
		try:
			instance = form.save(commit=False)
			#instance.master = Master.objects.get(pk=pk)
			instance.save()
			return HttpResponseRedirect( instance.go_to_starred() )
		except:
			return HttpResponseRedirect('/')
	context = {
		"form": form,
		"mas": mas,
	}
	return render(request, "edit_master_starred_only.html", context)


#edit just the prospect status for an existing master contact
@login_required
def edit_prospect_in_master(request, pk=None):
	mas = get_object_or_404(Master, pk=pk)
	form = MasterJustProspect(request.POST or None, request.FILES or None, instance=mas)
	if form.is_valid():
		try:
			instance = form.save(commit=False)
			#instance.master = Master.objects.get(pk=pk)
			instance.save()
			return HttpResponseRedirect( instance.go_to_prospects() )
		except:
			return HttpResponseRedirect('/')
	context = {
		"form": form,
		"mas": mas,
	}
	return render(request, "edit_master_prospect_only.html", context)


# add a new master contact
@login_required
def add_master_entry(request):
	form = MasterForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		try:
			instance = form.save(commit=False)
			#instance.master = Master.objects.get(pk=pk)
			instance.save()
			form.save_m2m() # this is essential - it saves the manytomany
			pri_group = form.cleaned_data.get("primary_group")
			pgroup = Group.objects.get(group_name=pri_group)
			return HttpResponseRedirect( instance.get_absolute_url() ) 
		except:
			return HttpResponseRedirect('/')
	context = {
		"form": form,
	}
	return render(request, "add_master.html", context)


# add a new touchpoint for existing contact
@login_required
def add_contact_touchpoint(request, pk=None):
	mas = get_object_or_404(Master, pk=pk)
	form = ContactForm(request.POST or None)
	if form.is_valid():
		try:
			instance = form.save(commit=False)
			#instance.master = Master.objects.get(pk=pk)
			instance.contact_name = Master.objects.get(pk=pk)
			instance.save()
			# form.save_m2m() # this is essential - it saves the manytomany
			# pri_group = form.cleaned_data.get("primary_group")
			# pgroup = Group.objects.get(group_name=pri_group)
			return HttpResponseRedirect( instance.get_absolute_url() )
		except:
			return HttpResponseRedirect('/')
	context = {
		"form": form,
		"mas": mas,
	}
	return render(request, "add_contact_touchpoint.html", context)


# Edit a touchpoint for an existing contact
@login_required
def edit_contact_touchpoint(request, pk=None, pk2=None):
	mas = get_object_or_404(Master, pk=pk)
	cont = get_object_or_404(Contact_log, pk=pk2)
	form = EditContactForm(request.POST or None, request.FILES or None, instance=cont)
	if form.is_valid():
		try:
			instance = form.save(commit=False)
			#instance.master = Master.objects.get(pk=pk)
			instance.save()
			return HttpResponseRedirect( instance.get_absolute_url() )
		except:
			return HttpResponseRedirect('/')
	context = {
		"form": form,
		"mas": mas,
		"cont": cont,
	}
	return render(request, "edit_contact_touchpoint.html", context)

########################################################################
########################################################################
#######################    CALENDAR VIEWS    ###########################
########################################################################
########################################################################

#SUMMARY VIEW FOR CALENDAR - shows due today 
@login_required
def calendar_forecast_today(request):
	m = Master.objects.filter(next_contact_date__isnull=False)  
	total_with_date = len(m)
	date_today = datetime.date.today()
	total_with_date_imp = len(m.filter(next_contact_date__lt = date_today + datetime.timedelta(days= 8) ))
	
	date_today_plus1 = date_today + datetime.timedelta(days= 1)
	date_today_plus2 = date_today + datetime.timedelta(days= 2)
	past_due = m.filter(next_contact_date__lt = date_today)
	past_due_total = len(past_due)
	list_today = m.filter(next_contact_date = date_today)
	list_today_total = len(list_today)
	list_today_plus1 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 1)  ))
	list_today_plus1_total = len(list_today_plus1)
	list_today_plus2 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 2)  ))
	list_today_plus2_total = len(list_today_plus2)
	future = m.filter(next_contact_date__gt = ( date_today + datetime.timedelta(days= 2)  ))
	future_total = len(future)
	
	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE next_contact_date =  DATE(now() - 8 * interval '1 hour')
	ORDER BY days_to_next_contact, importance_ranking,contact_date DESC''')
	#recent_reviews1 = cursor.fetchall() 
	filtered_list_details = dictfetchall(cursor)
	context = {
		"all_names": m,
		"total_with_date": total_with_date,
		"total_with_date_imp": total_with_date_imp,
		"date_today": date_today,
		"date_today_plus1": date_today_plus1,
		"date_today_plus2": date_today_plus2,
		"past_due": past_due,
		"past_due_total": past_due_total,
		"list_today": list_today,
		"list_today_total": list_today_total,
		"list_today_plus1": list_today_plus1,
		"list_today_plus1_total": list_today_plus1_total,
		"list_today_plus2": list_today_plus2,
		"list_today_plus2_total": list_today_plus2_total,
		"future": future,
		"future_total": future_total,
		"filtered_list_details": filtered_list_details,	
	}
	return render(request, 'calendar_forecast.html', context)

#SUMMARY VIEW FOR CALENDAR - shows past due
@login_required
def calendar_forecast_past_due(request):
	m = Master.objects.filter(next_contact_date__isnull=False)  
	total_with_date = len(m)
	date_today = datetime.date.today()
	total_with_date_imp = len(m.filter(next_contact_date__lt = date_today + datetime.timedelta(days= 8) ))

	date_today_plus1 = date_today + datetime.timedelta(days= 1)
	date_today_plus2 = date_today + datetime.timedelta(days= 2)
	past_due = m.filter(next_contact_date__lt = date_today)
	past_due_total = len(past_due)
	list_today = m.filter(next_contact_date = date_today)
	list_today_total = len(list_today)
	list_today_plus1 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 1)  ))
	list_today_plus1_total = len(list_today_plus1)
	list_today_plus2 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 2)  ))
	list_today_plus2_total = len(list_today_plus2)
	future = m.filter(next_contact_date__gt = ( date_today + datetime.timedelta(days= 2)  ))
	future_total = len(future)
	
	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE next_contact_date <  DATE(now() - 8 * interval '1 hour')
	ORDER BY days_to_next_contact, importance_ranking, contact_date DESC''')
	#recent_reviews1 = cursor.fetchall() 
	filtered_list_details = dictfetchall(cursor)
	context = {
		"all_names": m,
		"total_with_date": total_with_date,
		"total_with_date_imp": total_with_date_imp,
		"date_today": date_today,
		"date_today_plus1": date_today_plus1,
		"date_today_plus2": date_today_plus2,
		"past_due": past_due,
		"past_due_total": past_due_total,
		"list_today": list_today,
		"list_today_total": list_today_total,
		"list_today_plus1": list_today_plus1,
		"list_today_plus1_total": list_today_plus1_total,
		"list_today_plus2": list_today_plus2,
		"list_today_plus2_total": list_today_plus2_total,
		"future": future,
		"future_total": future_total,
		"filtered_list_details": filtered_list_details,	
	}
	return render(request, 'calendar_forecast_past_due.html', context)

#Summary view for calendar - shows plus 1
@login_required
def calendar_forecast_plus1(request):
	m = Master.objects.filter(next_contact_date__isnull=False)  
	total_with_date = len(m)
	date_today = datetime.date.today()
	total_with_date_imp = len(m.filter(next_contact_date__lt = date_today + datetime.timedelta(days= 8) ))
	
	date_today_plus1 = date_today + datetime.timedelta(days= 1)
	date_today_plus2 = date_today + datetime.timedelta(days= 2)
	past_due = m.filter(next_contact_date__lt = date_today)
	past_due_total = len(past_due)
	list_today = m.filter(next_contact_date = date_today)
	list_today_total = len(list_today)
	list_today_plus1 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 1)  ))
	list_today_plus1_total = len(list_today_plus1)
	list_today_plus2 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 2)  ))
	list_today_plus2_total = len(list_today_plus2)
	future = m.filter(next_contact_date__gt = ( date_today + datetime.timedelta(days= 2)  ))
	future_total = len(future)
	
	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE next_contact_date =  DATE(now() - 8 * interval '1 hour') + 1 * interval '1 day'
	ORDER BY days_to_next_contact, importance_ranking,contact_date DESC''')
	#recent_reviews1 = cursor.fetchall() 
	filtered_list_details = dictfetchall(cursor)
	context = {
		"all_names": m,
		"total_with_date": total_with_date,
		"total_with_date_imp": total_with_date_imp,
		"date_today": date_today,
		"date_today_plus1": date_today_plus1,
		"date_today_plus2": date_today_plus2,
		"past_due": past_due,
		"past_due_total": past_due_total,
		"list_today": list_today,
		"list_today_total": list_today_total,
		"list_today_plus1": list_today_plus1,
		"list_today_plus1_total": list_today_plus1_total,
		"list_today_plus2": list_today_plus2,
		"list_today_plus2_total": list_today_plus2_total,
		"future": future,
		"future_total": future_total,
		"filtered_list_details": filtered_list_details,	
	}
	return render(request, 'calendar_forecast_plus1.html', context)

#Summary view for calendar - shows plus 2
@login_required
def calendar_forecast_plus2(request):
	m = Master.objects.filter(next_contact_date__isnull=False)  
	total_with_date = len(m)
	date_today = datetime.date.today()
	total_with_date_imp = len(m.filter(next_contact_date__lt = date_today + datetime.timedelta(days= 8) ))

	
	date_today_plus1 = date_today + datetime.timedelta(days= 1)
	date_today_plus2 = date_today + datetime.timedelta(days= 2)
	past_due = m.filter(next_contact_date__lt = date_today)
	past_due_total = len(past_due)
	list_today = m.filter(next_contact_date = date_today)
	list_today_total = len(list_today)
	list_today_plus1 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 1)  ))
	list_today_plus1_total = len(list_today_plus1)
	list_today_plus2 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 2)  ))
	list_today_plus2_total = len(list_today_plus2)
	future = m.filter(next_contact_date__gt = ( date_today + datetime.timedelta(days= 2)  ))
	future_total = len(future)
	
	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE next_contact_date =  DATE(now() - 8 * interval '1 hour') + 2 * interval '1 day'
	ORDER BY days_to_next_contact, importance_ranking, contact_date DESC''')
	#recent_reviews1 = cursor.fetchall() 
	filtered_list_details = dictfetchall(cursor)
	context = {
		"all_names": m,
		"total_with_date": total_with_date,
		"total_with_date_imp": total_with_date_imp,
		"date_today": date_today,
		"date_today_plus1": date_today_plus1,
		"date_today_plus2": date_today_plus2,
		"past_due": past_due,
		"past_due_total": past_due_total,
		"list_today": list_today,
		"list_today_total": list_today_total,
		"list_today_plus1": list_today_plus1,
		"list_today_plus1_total": list_today_plus1_total,
		"list_today_plus2": list_today_plus2,
		"list_today_plus2_total": list_today_plus2_total,
		"future": future,
		"future_total": future_total,
		"filtered_list_details": filtered_list_details,	
	}
	return render(request, 'calendar_forecast_plus2.html', context)

#SUMMARY VIEW FOR CALENDAR - shows 3 days and beyond 
@login_required
def calendar_forecast_beyond(request):
	m = Master.objects.filter(next_contact_date__isnull=False)  
	total_with_date = len(m)
	date_today = datetime.date.today()
	total_with_date_imp = len(m.filter(next_contact_date__lt = date_today + datetime.timedelta(days= 8) ))
	
	date_today_plus1 = date_today + datetime.timedelta(days= 1)
	date_today_plus2 = date_today + datetime.timedelta(days= 2)
	past_due = m.filter(next_contact_date__lt = date_today)
	past_due_total = len(past_due)
	list_today = m.filter(next_contact_date = date_today)
	list_today_total = len(list_today)
	list_today_plus1 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 1)  ))
	list_today_plus1_total = len(list_today_plus1)
	list_today_plus2 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 2)  ))
	list_today_plus2_total = len(list_today_plus2)
	future = m.filter(next_contact_date__gt = ( date_today + datetime.timedelta(days= 2)  ))
	future_total = len(future)
	
	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,		
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE next_contact_date >  DATE(now() - 8 * interval '1 hour') + 2 * interval '1 day'
	ORDER BY days_to_next_contact, importance_ranking, contact_date DESC''')
	#recent_reviews1 = cursor.fetchall() 
	filtered_list_details = dictfetchall(cursor)
	context = {
		"all_names": m,
		"total_with_date": total_with_date,
		"total_with_date_imp": total_with_date_imp,
		"date_today": date_today,
		"date_today_plus1": date_today_plus1,
		"date_today_plus2": date_today_plus2,
		"past_due": past_due,
		"past_due_total": past_due_total,
		"list_today": list_today,
		"list_today_total": list_today_total,
		"list_today_plus1": list_today_plus1,
		"list_today_plus1_total": list_today_plus1_total,
		"list_today_plus2": list_today_plus2,
		"list_today_plus2_total": list_today_plus2_total,
		"future": future,
		"future_total": future_total,
		"filtered_list_details": filtered_list_details,	
	}
	return render(request, 'calendar_forecast_beyond.html', context)

#SUMMARY VIEW FOR CALENDAR - shows all by date
@login_required
def calendar_forecast_all(request):
	m = Master.objects.filter(next_contact_date__isnull=False)  
	total_with_date = len(m)
	date_today = datetime.date.today()
	total_with_date_imp = len(m.filter(next_contact_date__lt = date_today + datetime.timedelta(days= 8) ))
	
	date_today_plus1 = datetime.date.today() + datetime.timedelta(days= 1)
	date_today_plus2 = datetime.date.today() + datetime.timedelta(days= 2)
	past_due = m.filter(next_contact_date__lt = date_today)
	past_due_total = len(past_due)
	list_today = m.filter(next_contact_date = date_today)
	list_today_total = len(list_today)
	list_today_plus1 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 1)  ))
	list_today_plus1_total = len(list_today_plus1)
	list_today_plus2 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 2)  ))
	list_today_plus2_total = len(list_today_plus2)
	future = m.filter(next_contact_date__gt = ( date_today + datetime.timedelta(days= 2)  ))
	future_total = len(future)
	
	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,		
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE next_contact_date IS NOT NULL
	ORDER BY days_to_next_contact, importance_ranking, contact_date DESC''')
	#recent_reviews1 = cursor.fetchall() 
	filtered_list_details = dictfetchall(cursor)
	context = {
		"all_names": m,
		"total_with_date": total_with_date,
		"total_with_date_imp": total_with_date_imp,
		"date_today": date_today,
		"date_today_plus1": date_today_plus1,
		"date_today_plus2": date_today_plus2,
		"past_due": past_due,
		"past_due_total": past_due_total,
		"list_today": list_today,
		"list_today_total": list_today_total,
		"list_today_plus1": list_today_plus1,
		"list_today_plus1_total": list_today_plus1_total,
		"list_today_plus2": list_today_plus2,
		"list_today_plus2_total": list_today_plus2_total,
		"future": future,
		"future_total": future_total,
		"filtered_list_details": filtered_list_details,	
	}
	return render(request, 'calendar_forecast_all.html', context)

#SUMMARY VIEW FOR CALENDAR - shows all by date and importance - filtered for 7 days
@login_required
def calendar_forecast_all_by_import(request):
	m = Master.objects.filter(next_contact_date__isnull=False)  
	total_with_date = len(m)
	date_today = datetime.date.today()
	total_with_date_imp = len(m.filter(next_contact_date__lt = date_today + datetime.timedelta(days= 8) ))
	
	date_today_plus1 = date_today + datetime.timedelta(days= 1)
	date_today_plus2 = date_today + datetime.timedelta(days= 2)
	past_due = m.filter(next_contact_date__lt = date_today)
	past_due_total = len(past_due)
	list_today = m.filter(next_contact_date = date_today)
	list_today_total = len(list_today)
	list_today_plus1 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 1)  ))
	list_today_plus1_total = len(list_today_plus1)
	list_today_plus2 = m.filter(next_contact_date = ( date_today + datetime.timedelta(days= 2)  ))
	list_today_plus2_total = len(list_today_plus2)
	future = m.filter(next_contact_date__gt = ( date_today + datetime.timedelta(days= 2)  ))
	future_total = len(future)
	
	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,		
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE next_contact_date IS NOT NULL AND importance_ranking = 1 AND (next_contact_date - DATE(now() - 8 * interval '1 hour')) < 8
	ORDER BY days_to_next_contact, importance_ranking, contact_date DESC''')
	filtered_list_rank_1 = dictfetchall(cursor)

	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,		
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE next_contact_date IS NOT NULL AND importance_ranking = 2 AND (next_contact_date - DATE(now() - 8 * interval '1 hour')) < 8
	ORDER BY days_to_next_contact, importance_ranking, contact_date DESC''')
	filtered_list_rank_2 = dictfetchall(cursor)

	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name, 
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,		
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE next_contact_date IS NOT NULL AND importance_ranking = 3 AND (next_contact_date - DATE(now() - 8 * interval '1 hour')) < 8
	ORDER BY days_to_next_contact, importance_ranking, contact_date DESC''')
	filtered_list_rank_3 = dictfetchall(cursor)

	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE next_contact_date IS NOT NULL AND importance_ranking = 4 AND (next_contact_date - DATE(now() - 8 * interval '1 hour')) < 8
	ORDER BY days_to_next_contact, importance_ranking, contact_date DESC''')
	filtered_list_rank_4 = dictfetchall(cursor)

	context = {
		"all_names": m,
		"total_with_date": total_with_date,
		"total_with_date_imp": total_with_date_imp,
		"date_today": date_today,
		"date_today_plus1": date_today_plus1,
		"date_today_plus2": date_today_plus2,
		"past_due": past_due,
		"past_due_total": past_due_total,
		"list_today": list_today,
		"list_today_total": list_today_total,
		"list_today_plus1": list_today_plus1,
		"list_today_plus1_total": list_today_plus1_total,
		"list_today_plus2": list_today_plus2,
		"list_today_plus2_total": list_today_plus2_total,
		"future": future,
		"future_total": future_total,
		"filtered_list_rank_1": filtered_list_rank_1,	
		"filtered_list_rank_2": filtered_list_rank_2,	
		"filtered_list_rank_3": filtered_list_rank_3,	
		"filtered_list_rank_4": filtered_list_rank_4,	
	}
	return render(request, 'calendar_forecast_all_by_imp.html', context)

#list of starred folks
@login_required
def list_of_starred(request):
	m = Master.objects.filter(starred=True)  
	number_starred = len(m)
	date_today = datetime.date.today()

	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		notes,
		city,
		starred, 
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE starred = True
	ORDER BY importance_ranking, days_to_next_contact, contact_date DESC''')
	#recent_reviews1 = cursor.fetchall() 
	filtered_list_details = dictfetchall(cursor)
	
	flist2 = filtered_list_details[1:] #a second list for border formatting purposes


	context = {
		"all_names": m,
		"number_starred": number_starred,
		"date_today": date_today,	
		"filtered_list_details": filtered_list_details,	
		"flist2": flist2, #delete if this doesnt work	
	}
	return render(request, 'list_of_starred_folks.html', context)


#list of prospects
@login_required
def list_of_prospects(request):
	m = Master.objects.filter(prospect=True)  
	number_prospects = len(m)
	date_today = datetime.date.today()

	cursor = connection.cursor()
	cursor.execute(
	'''SELECT  DISTINCT 
		A.id AS master_id,
		group_name,
		first_name,
		last_name,
		next_contact_date,
		CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END AS imp_rating,
		importance_ranking,
		notes,
		city,
		starred,
		prospect,
		contact_date AS last_contact,
		(DATE(now() - 8 * interval '1 hour') - contact_date) AS days_since_last_contact,
		(next_contact_date - DATE(now() - 8 * interval '1 hour')) AS days_to_next_contact,
		next_contact_date AS next_contact_date,
		num_contacts AS total_num_of_contacts
	FROM  master_Master AS A
	INNER JOIN  
	(SELECT  contact_name_id,
	MAX(contact_date) AS contact_date,
	COUNT(contact_date) AS num_contacts
	FROM contact_contact_log
	GROUP BY contact_name_id) AS B ON A.id = B.contact_name_id 
	LEFT JOIN  p_groups_group AS C ON A.primary_group_id = C.id
    LEFT JOIN master_importance AS D ON (CASE WHEN A.ind_imp_rating IS NOT NULL THEN A.ind_imp_rating ELSE C.group_imp_rating END) = D.importance_descrip
    WHERE prospect = True
	ORDER BY importance_ranking, days_to_next_contact, contact_date DESC''')
	#recent_reviews1 = cursor.fetchall() 
	filtered_list_details = dictfetchall(cursor)

	context = {
		"all_names": m,
		"number_prospects": number_prospects,
		"date_today": date_today,	
		"filtered_list_details": filtered_list_details,	
	}
	return render(request, 'list_of_prospects.html', context)



def dateTimeViewBootstrap3(request):
    form = testForm2()
    return render(request, 'example.html', {
             'form': form,'bootstrap':3
            })


# #this one uses django tables
# def testview(request):
# 	table = MasterTable(Master.objects.all())
# 	RequestConfig(request).configure(table)
# 	context = {
# 	'table': table,
# 	}
# 	return render(request, 'test.html', context)

#this view uses jquery datatables
def testview2(request):
	table = Master.objects.all()
	context = {
	'table': table,
	}
	return render(request, 'test2.html', context)
