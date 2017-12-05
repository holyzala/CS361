from django.contrib import admin
from .models import TimeDelta, Team, Landmark, Game

admin.site.register(Team)
admin.site.register(TimeDelta)
admin.site.register(Landmark)
admin.site.register(Game)
