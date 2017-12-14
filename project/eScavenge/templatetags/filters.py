from django import template
from ..models import GMFactory
from datetime import timedelta

GM = GMFactory().get_gm()

register = template.Library()


@register.filter
def remove_milliseconds(timedelta):
    return str(timedelta).split('.')[0]

@register.filter
def total_time(teamhistory):
    totaltime = timedelta(days=0)
    for stat in teamhistory:
        totaltime += stat.time_delta
    return str(totaltime).split('.')[0]
