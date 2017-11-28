from django.contrib import admin
from .models import HuntUser
from .models import HuntCommand

admin.site.register(HuntUser)
admin.site.register(HuntCommand)

