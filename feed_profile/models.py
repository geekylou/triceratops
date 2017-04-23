from django.db import models
from django.contrib.postgres.fields import JSONField,ArrayField
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
import utils.markdown
import triceratops.settings

# Create your models here.

@python_2_unicode_compatible
class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    #liked = models.BooleanField(default=False)
    content_type = models.CharField(default="text/x-markdown",max_length=64)
    metadata = JSONField(default="",blank=True)
    tags = ArrayField(models.CharField(max_length=128, blank=True),default=[],blank=True)

#    search_vector_description = SearchVectorField(description)

    def html(self):
        return utils.markdown.to_html(self.description,self.content_type)

    def get_url(self):
         return triceratops.settings.BASE_URL+'profile/'+self.user.username

    def __str__(self):
        return str(self.user)
    def dict(self):
        return {
            'description': self.description,
            'description_type': self.content_type,
        }

