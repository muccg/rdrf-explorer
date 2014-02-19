from django.db import models
from django.core.urlresolvers import reverse


class Query(models.Model):
    title = models.CharField(max_length=255)
    database = models.CharField(max_length=255)
    collection = models.CharField(max_length=255)
    criteria = models.TextField()
    projection = models.TextField()
    description = models.TextField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('viewer_query', kwargs={'query_id': self.pk})

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Queries'

    def __unicode__(self):
        return unicode(self.title)
