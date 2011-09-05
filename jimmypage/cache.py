import urllib
import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.db.models import get_model
from django.http import HttpResponse
from django.utils import translation
from django.utils.encoding import iri_to_uri
from django.utils.hashcompat import md5_constructor

logger = logging.getLogger("jimmypage")

__all__ = ('cache_page', 'clear_cache')

DISABLED = getattr(settings, 'JIMMY_PAGE_DISABLED', False)
WATCHLIST = set(get_model(*app_model.split('.')) for app_model in getattr(settings, 'JIMMY_PAGE_WATCHLIST', []))
GLOBAL_GENERATION = "generation"

def clear_cache():
    logger.debug("incrementing generation")
    try:
        cache.incr(GLOBAL_GENERATION)
    except ValueError:
        cache.set(GLOBAL_GENERATION, 1)

def expire_cache(sender, instance, **kwargs):
    if instance.__class__ in WATCHLIST:
        logger.debug("%s has been updated, incrementing generation" % instance.__class__)
        clear_cache()

post_save.connect(expire_cache)
pre_delete.connect(expire_cache)

class cache_page(object):
    """
    Decorator to invoke cacheing for a view.  Can be used either this way::

        # uses default cache timeout
        @cache_page
        def my_view(request, ...):
            ...

    or this way::

        # uses 60 seconds as cache timeout
        @cache_page(60)
        def my_view(request, ...):
            ...

    """
    def __init__(self, arg=None):
        if callable(arg):
            # we are called with a function as argument; e.g., as a bare
            # decorator.  __call__ should be the new decorated function.
            self.call = self.decorate(arg)
            self.time = None

        else:
            # we are called with an argument.  __call__ should return
            # a decorator for its argument.
            if arg is not None:
                self.time = arg
            self.call = self.decorate

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def decorate(self, f):
        self.f = f
        return self.decorated

    def decorated(self, request, *args, **kwargs):
        if request_is_cacheable(request):
            key = get_cache_key(request)
            cached = cache.get(key)
            if cached is not None:
                logger.debug("serving request from cache (%s)" % key)
                (content, content_type) = cached
                res = HttpResponse(content=content, content_type=content_type)
                res["ETag"] = key
                return res

            response = self.f(request, *args, **kwargs)
            if response_is_cacheable(request, response):
                logger.debug("storing response in cache (%s)" % key)
                content = response.content
                content_type = dict(response.items()).get("Content-Type")
                if self.time is not None:
                    cache.set(key, (content, content_type), self.time)
                else:
                    cache.set(key, (content, content_type))
            else:
                logger.debug("response wasn't cacheable, not storing")

            response["ETag"] = key
            return response

        logger.debug("request wasn't cacheable")
        return self.f(request, *args, **kwargs)

def get_cache_key(request):
    user_id = ""
    try:
        if request.user.is_authenticated():
            user_id = str(request.user.id)
    except AttributeError: # e.g. if auth is not installed
        pass

    bits = {
        "generation": str(cache.get(GLOBAL_GENERATION)),
        "path": iri_to_uri(request.path),
        "get_params": urllib.urlencode(request.GET),
        "language": translation.get_language(),
        "user_id": str(user_id),
    }

    key = ":".join([
        bits["generation"],
        bits["path"],
        bits["get_params"],
        bits["language"],
        bits["user_id"]])

    digest = md5_constructor(key).hexdigest()

    logger.debug("generating cache key: %r (%s)" % (bits, digest))

    return digest

def request_is_cacheable(request):
    return (not DISABLED) and \
            request.method == "GET" and \
            len(messages.get_messages(request)) == 0

def response_is_cacheable(request, response):
    return (not DISABLED) and \
        response.status_code == 200 and \
        response.get('Pragma', None) != "no-cache" and \
        response.get('Vary', None) != "Cookie" and \
        not request.META.get("CSRF_COOKIE_USED", None)

clear_cache()
