
from django import template
from ..CLI import CLI, COMMANDS
from ..models import GMFactory, Team, Landmark, LandmarkStat

GM = GMFactory().get_gm()

register = template.Library()

@register.filter
def getTeamGame(username):
    try:
        user = Team.objects.get(username=username)
    except Team.DoesNotExist:
        return "No Game Running"
    if user.game_id is None:
        return "No Game Running"
    return user.game_id

@register.filter
def getTeamPoints(username):
    user = Team.objects.get( username=username )
    points = user.points
    return points
