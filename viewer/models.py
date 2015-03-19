from django.db import models
from django.core.urlresolvers import reverse

from rdrf.models import Registry


class Query(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    
    registry = models.ForeignKey(Registry)
    
    collection = models.CharField(max_length=255, default="cdes")
    criteria = models.TextField(blank=True, null=True)
    projection = models.TextField(blank=True, null=True)
    
    sql_query = models.TextField()
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('viewer_query', kwargs={'query_id': self.pk})

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Queries'

    def __unicode__(self):
        return unicode(self.title)
