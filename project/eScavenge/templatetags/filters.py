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


@register.filter
def get_all_teams(game):
    return game.teams.all()


@register.filter
def get_all_landmarks(game):
    return game.landmarks.all()


@register.filter
def get_status(game):
    if game.ended:
        return 2
    if game.started:
        return 1
    return 0


@register.filter
def zero_if_none(timer):
    if timer is None:
        return timedelta(0)
    return timer
