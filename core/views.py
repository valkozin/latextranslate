import datetime
import functools
import inspect
import json
import traceback

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View

from django.conf import settings

from django.http import HttpResponse

import logging

logger = logging.getLogger('main_app')

JSON_DUMPS_PARAMS = {
    'ensure_ascii': False
}


def ret(json_object, status=200):
    return JsonResponse(
        json_object,
        status=status,
        safe=not isinstance(json_object, list),
        json_dumps_params=JSON_DUMPS_PARAMS
    )


def error_response(exception):
    res = {"errorMessage": str(exception),
           "traceback": traceback.format_exc()}
    if settings.DEBUG:
        # return ret(res, status=400)
        logger.exception('test')
        return HttpResponse('Something went wrong. We are working on it. Please try again later.<br> '
                            '<a href="/">homepage</a>')


def base_view(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            with transaction.atomic():
                return fn(request, *args, **kwargs)
        except Exception as e:
            return error_response(e)

    return inner
