from django import template

register = template.Library()

@register.filter(name='length_is')
def length_is(value, arg):
    """Returns True if the value has the given length."""
    return len(value) == int(arg)