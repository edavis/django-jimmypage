from django.core.cache.backends import memcached

class MemcachedCache(memcached.MemcachedCache):
    def _get_memcached_timeout(self, timeout=None):
        """Custom memcache backend so we can use 0 as a timeout.

        In memcached, setting `0` for a timeout sets it to never expire.

        But Django's default memcached caching backends treat 0 as
        False, returning the default timeout (300 seconds) instead of
        accepting zero.
        """
        # https://code.djangoproject.com/ticket/9595 for more on this
        if timeout == 0: return 0
        return super(MemcachedCache, self)._get_memcached_timeout(timeout)
