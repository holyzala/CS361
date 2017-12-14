from django import template
from ..models import GMFactory
from datetime import timedelta

from functools import reduce

GM = GMFactory().get_gm()

register = template.Library()


@register.filter
def remove_milliseconds(timedelta):
    return str(timedelta).split('.')[0]


@register.filter
def total_time(team_history):
    return reduce(lambda x, y: x + y.time_delta, team_history, timedelta(0))
