from django import template

register = template.Library()

@register.filter
def integer_comparison(value, arg):
    print "made it to here"
    print value, arg
    if value == arg:
        print value, arg
        return True
    else:
        return False


