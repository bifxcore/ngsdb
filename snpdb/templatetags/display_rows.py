from django import template

register = template.Library()


@register.filter
def group_by(value, arg):
    return grouped(value, arg)


def grouped(l, n):
    # Yield successive n-sized chunks from l.
    for i in xrange(0, len(l), n):
        yield l[i:i+n]