from django import template

register = template.Library()


@register.filter
def empty_effect(value):
	if value:
		return False
	else:
		return True

register.filter(empty_effect)

@register.filter
def no_effect(value):
	if value == 'None' or value is None:
		return False
	else:
		return True


@register.filter
def get_type(value):
	if type(value) is list:
		return True
	else:
		return False

@register.filter
def get_value_type(value, arg):
	if arg == 'int':
		if isinstance(value, int):
			return True
		else:
			return False


@register.filter
def get_type_value(value):
	print type(value), value
	return type(value)


def zero(value):
	if int(value) == 0:
		return False
	else:
		return True

register.filter(zero)

@register.filter
def sum_dict(value):
	sums = 0
	for key, val in value:
		if isinstance(val, int):
			sums += val
	return sums

@register.filter
def effect_type_title(title):
	new = title.replace('_', ' ').title()
	return new

@register.filter
def joinby(value, arg):
    return arg.join(value)