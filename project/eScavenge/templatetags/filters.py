from django import template
from ..models import GMFactory

GM = GMFactory().get_gm()

register = template.Library()


@register.filter
def remove_milliseconds(timedelta):
    return str(timedelta).split('.')[0]
