from django.forms import ModelForm
from models import Query


class QueryForm(ModelForm):

    class Meta:
        model = Query
        fields = ['id', 'title', 'database', 'collection',
                  'criteria', 'projection', 'description', 'created_by']
