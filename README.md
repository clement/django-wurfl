django-wurfl in 15 seconds
==========================

How to install it
-----------------

### Dependencies

django-wurfl use the *python-Levenshtein* package. However, the hosting site is defunct, so

    john@doe:~# sudo easy_install python-Levenshtein

probably won't work. You can however still get the source code from
[Michael Noll's website](http://www.michael-noll.com/wiki/Python-Levenshtein)
and install it manually.


### Setup

Put the `wurfl` folder somewhere on your python path. Then add in your settings
file :

    # in settings.py
    INSTALLED_APPS = (
        ...
        'wurfl',
        ...
    )

Create the database tables with `syncdb` command. Then import WURFL data in the
database using the custom command:

    john@doe:~/mydjangoproject/# ./manage.py wurfl-load <path/to/wurfl.xml>

How to use it
-------------

django-wurfl provides a middleware, a decorator, and a context processor for you
to use in your django powered application.

How to use the middleware :

    # Add the middleware in your settings.py file
    MIDDLEWARE_CLASSES = (
        ...
        'wurfl.middleware.DeviceMiddleware',
        ...
    )

    # You can now access the detected device in your views
    def myview(request):
        markup_dict = request.device['markup'] # this is a group of
                # capabilities stored represented as a dictionnary

        if request.device['html_wi_w3_xhtmlbasic']:
            # this is a single capability
            # in this case, equivalent to markup_dict['html_wi_w3_xhtmlbasic']
            pass


The decorators allows you to activate the device detection only in specific
views, whereas the middleware is application wide.

    # In your views
    from wurfl.decorators import device

    @device
    def myview(request):
        if request.device['html_wi_w3_xhtmlbasic']:
            # bla bla bla
    
And the context processor is helpful to have the device variable directly
accessible in your template (if the device has been detected before hand
using the middleware or a decorator).

    # Add the context processor in your settings.py file
    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        "wurfl.context_processors.device",
        ...
    )

    # Use the device in your templates
    <p>Markup xhtmlbasic : {{ device.html_wi_w3_xhtmlbasic }}</p>


Reference
=========

Settings reference
------------------

- `WURFL_USE_CACHE` : if set to True, django-wurfl will use Django cache backend
    to cache user agents and associated capabilities. That will give a
    significant performance boost to your mobile application, and is highly
    recommended. See also `WURFL_CACHE_PREFIX` and `WURFL_CACHE_TIMEOUT`.
    Default to `False`.
- `WURFL_CACHE_PREFIX` : Cache key in django-wurfl are user agent's MD5
    hexadecimal digest. In order to prevent cache key collision, all keys are
    prefixed with the string in this setting (default to `'wurfl_'`).
- `WURFL_CACHE_TIMEOUT` : timeout (in seconds) for cached user agent
    capabilities. If set to `None`, it will use the default timeout of your
    application. If set to `0`, the cached values will never expire. Default to
    `None`.
> Note:
> 
> The cache is not automatically invalidated when you update your WURFL data
> (patches, or main files), it is your responsibility to do so, or to set a
> relevant timeout value.

- `WURFL_USE_PATCH` : if set to `True`, django-wurfl will take in account the
    patches to calculate the capabilities of the detected device. The patched
    capabilities are pre-processed using the `wurfl-hybrid` command (see below)
    Default to `False`.
- `WURFL_URL` : the url to the XML wurfl file, not used in this version.
- `WURFL_UA_PREFIX_MATCHING` : if set to `True`, django-wurfl will search for
    the device using only a prefix of the user agent in case it can't find the
    exact user agent in the database. Default to `False`.
- `WURFL_UA_PREFIX_MATCHING_MAX_DISTANCE` : when searching with only a prefix
    of the user_agent, this setting is used to limit the sensitivity of the
    search. It indicates the maximum [Levenshtein Distance][] that will be
    tolerated between the original user agent and the search results. Default
    to `20`.

Commands reference
------------------

- `wurfl-load` : load the data from a wurfl file and store it in the database.
    Takes 1 argument, the path to the WURLF XML file.
- `wurfl-hybrid` : apply the patch to the current wurfl data and store the
    result in the hybrid table.
- `wurfl-add-patch` : create a new patch from an XML file. You can also do that
    using the administration back office. See the documentation of this command
    for more information.

[Levenshtein Distance]: http://en.wikipedia.org/wiki/Levenshtein_distance
