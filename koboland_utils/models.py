from django.db import models

from koboland_utils.fields import make_id


class BaseModel(models.Model):
    id = models.BigIntegerField(default=make_id, primary_key=True)

    class Meta:
        abstract = True
