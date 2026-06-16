from django import template
import math

register = template.Library()

@register.filter
def reading_time(text):
    words_per_minute = 200
    word_count = len(text.split())
    minutes = math.ceil(word_count / words_per_minute)
    return minutes if minutes > 0 else 1

@register.filter
def divideby(value, arg):
    try:
        return int(value) // int(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def split_keywords(value):
    if not value:
        return []
    return [k.strip() for k in value.split(',') if k.strip()]
