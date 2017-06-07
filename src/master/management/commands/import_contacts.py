from django.core.management.base import BaseCommand, CommandError
import csv
from master.models import Master
from p_groups.models import Group
from tags.models import Tag
import datetime 


class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('csv_file', nargs='+', type=str)

	def handle(self, *args, **options):
		for csv_file in options['csv_file']:
			dataReader = csv.reader(open(csv_file), delimiter=',', quotechar='"')
			for row in dataReader:
				con = Master()
				con.first_name = row[0]
				con.last_name = row[1]
				con.email = row[2]
				con.workplace = row[3]
				con.title = row[4]
				starred1 = row[5]
				if starred1 == 'TRUE':
					con.starred = True
				else:
					con.starred = False
				prim_group = Group.objects.get(group_name=row[6])  #first get class name
				con.primary_group = prim_group
				con.city = row[7]
				con.first_met = datetime.datetime.strptime(row[8], '%m/%d/%Y').date()
				con.ind_imp_rating = row[9]
				con.target_contact_cycle_individual = row[10]
				dont_update = row[11]
				if dont_update == 'TRUE':
					con.dont_update_next_contact_date = True
				else:
					con.dont_update_next_contact_date = False
				con.save()
				#code to pull in tags when not blank
				try:
					tag_pulled = Tag.objects.get(tag_name=row[12])
					con.tag1.add(tag_pulled)
				except:
					pass
				self.stdout.write(
					'Created contact {} {}'.format(con.first_name, con.last_name)
				)