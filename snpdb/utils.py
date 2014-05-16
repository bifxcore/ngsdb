__author__ = 'mcobb'
from urlparse import urlparse, urlunparse
from django.http import QueryDict
import re


def url_append_parameter(url, attr, val):
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    query_dict = QueryDict(query).copy()
    query_dict[attr] = val
    query = query_dict.urlencode()
    return urlunparse((scheme, netloc, path, params, query, fragment))


def build_orderby_urls(url, attributes):
    urls = {}
    for attr in attributes:
        urls[attr] = url_append_parameter(url, "order_by", attr)
    return urls


def integer_filters(results_list, filter_by, selection):
    return_list = []
    for each in results_list:
        field = each[0]
        if bool(re.search(filter_by, str(field))):
            return_list.append(field)
    print return_list
    return return_list


def subtract_values(arg1, arg2):
    return abs(arg1-arg2)