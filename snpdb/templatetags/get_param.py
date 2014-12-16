from django import template
register = template.Library()

@register.simple_tag
def add_get_param(request, attr, val):
	dict_ = request.GET.copy()
	dict_[attr] = val

	return dict_.urlencode()