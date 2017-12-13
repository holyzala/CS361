from django import template
from ..CLI import CLI, COMMANDS
from ..models import GMFactory, Team, Landmark, LandmarkStat

GM = GMFactory().get_gm()

register = template.Library()


@register.filter
def remove_milliseconds(timedelta):
    return str(timedelta).split('.')[0]


@register.filter
def getTeamPoints(username):
    user = Team.objects.get( username=username )
    points = user.points
    return points
