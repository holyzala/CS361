from django.db import models
class HuntUser(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)

class HuntCommand(models.Model):
    def __str__(self):
        return self.text
    text = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(HuntUser)
# Create your models here.
