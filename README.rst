django-jimmypage
================

Jimmy Page is a generational caching app for Django.

*"There are only two hard things in Computer Science: cache
invalidation and naming things."* - Phil Karlton

What is Generational Caching?
-----------------------------

So how do generational and "regular" caching differ?  The biggest
difference is how they handle stale content.

Regular caching is designed so that after *N* seconds, the cached
content expires.  Then, once expired, the next request comes along and
-- finding the cached content newly expired -- repopulates it with
(potentially) fresher content.

It's not hard to see the downsides to this method.  You're constantly
trying to find a balance between setting that *N* too low (which gives
you fresher content at the expense of hammering your database) and too
high (which eases off your database but increases the chance of
serving stale content).  But beyond that, what if the content hasn't
changed since it was cached?  Why keep hitting a database looking for
fresh content when there isn't anything fresher?

**Wouldn't it just make more sense to keep serving the cached content
until you have a reason not to?**

That's where generational caching comes in.

The central feature in generational caching is something called a
"generation."  It's just a number -- stored in your cache -- that you
increment whenever you want to invalidate items in your cache.

The idea is to increment this generation number whenever you add,
update, or delete a record in your database.

When building your cache keys, you include this generation number in
the key. As long as the generation number stays the same, the key will
continue serve the same content.  But when you increment the
generation -- say, after adding a database record -- all cache keys
that include the generation number become transparently invalidated.
Now all future requests will use this new generation number when
generating their cache keys, TK.

This technique gives you the best of both possible worlds: fresh
content and low database loads.

Example
-------

But let's say you have a newspaper website and whenever a new article
is published, you want everything to update.

This technique provides easy whole-page caching, with an assurance
that no part of the site will ever contain stale content.  The
conservative approach to expiration allows Jimmy to function in a
drop-in manner, without any domain-specific knowledge of how data
updates might affect the output of views.  It will greatly speed up
slowly updated sites, especially when used in combination with Johnny
Cache and carefully designed, more aggressive caching for particularly
intensive views.  This technique is not likely to be effective in
sites that have a high ratio of database writes to reads.

Installation
------------

set up a watchlist (install?)

This is the first, as yet largely untested alpha release.  Some notes:

* In order to function properly, `Johnny Cache
  <http://packages.python.org/johnny-cache/>`_ should be installed and used.
  Johnny Cache patches the Django caching framework to allow caching with
  infinite timeouts, something that this app does not provide alone.  If you
  don't want to use Johnny Cache, you should set the
  ``JIMMY_PAGE_CACHE_SECONDS`` setting to something other than 0.
* If you have any custom SQL that updates the database without emitting
  ``post_save`` or ``pre_delete`` signals, things might get screwy.  At this
  stage, Jimmy Page works best with sites using vanilla ORM calls.

Install using pip::

    pip install -e git://github.com/yourcelf/django-jimmypage.git#egg=django-jimmypage

or clone the git archive and use setup.py::

    python setup.py install

Usage
-----

To use, include ``jimmypage`` in your INSTALLED_APPS setting, and define
``JIMMY_PAGE_CACHE_PREFIX`` in your settings.py file::

    # settings.py
    INSTALLED_APPS = (
        ...
        "jimmypage",
        ...
    )
    JIMMY_PAGE_CACHE_PREFIX = "jp_mysite"

To cache a view, use the ``cache_page`` decorator::

    from jimmypage.cache import cache_page

    @cache_page
    def myview(request):
        ...

Any update to any table will clear the cache (by incrementing the generation),
unless the tables are included in the ``JIMMY_PAGE_EXPIRATION_WHITELIST``.  The
defaults can be overridden by defining it in your settings.py.  By default it
includes::

    JIMMY_PAGE_EXPIRATION_WHITELIST = [
        "django_session",
        "django_admin_log",
        "registration_registrationprofile",
        "auth_message",
        "auth_user",
    ]

Views are cached on a per-user, per-language, per-path basis.  Anonymous users
share a cache, but authenticated users get a separate cache, ensuring that no
user will ever see another's user-specific content.  The cache is only used if:

* The request method is ``GET``
* There are no `messages
  <http://docs.djangoproject.com/en/dev/ref/contrib/messages/>`_ stored for
  the request
* The response status is 200
* The response does not contain a ``Pragma: no-cache`` header

Please contribute any bugs or improvements to help make this better!

TODO
----

Current TODOs include:

* Much more testing, analysis, and code review
* middleware to apply the caching to everything, and a decorator to exclude
  particular views
* Hooks into Django Debug Toolbar to make debugging easier
