
import django_tables2 as tables
from .models import Master

class MasterTable(tables.Table):
    class Meta:
        model = Master
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}
        fields = ['pk','first_name','last_name','city','primary_group']