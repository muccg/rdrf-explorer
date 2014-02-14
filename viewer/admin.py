from django.contrib import admin
from models import Query

from django.contrib import admin

class QueryAdmin(admin.ModelAdmin):
    list_display = ('title', 'database', 'collection', 'description', 'created_by', 'created_at')
    list_filter = ('title',)

admin.site.register(Query, QueryAdmin)
