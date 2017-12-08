from django.contrib import admin
from .models import LandmarkStat, Team, Landmark, Game

admin.site.register(Team)
admin.site.register(LandmarkStat)
admin.site.register(Landmark)
admin.site.register(Game)
