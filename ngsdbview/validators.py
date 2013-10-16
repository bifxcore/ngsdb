from django.core.exceptions import ValidationError
import re

def validate_librarycode(value):
    pattern = re.compile(r'^\u{2}\d{3}$')
    if not re.match(pattern,value):
       raise ValidationError(u'%s is not a library code' % value)
