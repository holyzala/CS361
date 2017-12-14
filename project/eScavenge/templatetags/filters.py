from django import template
from ..models import GMFactory
import datetime
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import Coalesce

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