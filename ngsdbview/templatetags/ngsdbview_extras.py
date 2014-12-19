from django import template

register = template.Library()




def hash(h,key):
    if key in h:
        return h[key]
    else:
        return None

register.filter(hash)





def keyExists(h, key):
    if key in h:
        return True
    else:
        return False

register.filter(keyExists)


def hash2libcode(h,key):
    if key in h:
        return h[key].librarycode
    else:
        return None

register.filter(hash2libcode)


def mod(value1, value2):
    list = divmod(value1, value2)
    return list[1]

register.filter(mod)

def quotient(value1, value2):
    list = divmod(value1, value2)
    return list[0]

register.filter(quotient)