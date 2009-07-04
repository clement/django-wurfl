class FieldSubscript(object):
    """
    Dirty hack-class for allowing access to fields from
    a model inside a template (see admin/change_form)
    without having to go for the templatetags like it's
    done in the original admin site.
    
    The class is bound to a model, and define just
    the read [] operator, getting a field from the model
    _meta class based on its name
    """
    model = None
    
    def __init__(self, model):
        self.model = model
        
    def __getitem__(self, key):
        try:
            return self.model._meta.get_field(key)
        except:
            return None
            

import datetime
import time
from django.utils.translation import ungettext, ugettext

def pretty_duration(duration):
    """
    Takes a duration in seconds and return a nicely formatted string,
    e.g. "10 minutes". If the duration is negative, then "0 seconds"
    is returned.

    Units used are years, months, weeks, days, hours, minutes and seconds.
    Up to two adjacent units will be displayed.  For example,
    "2 weeks, 3 days" and "1 year, 3 months" are possible outputs, but
    "2 weeks, 3 hours" and "1 year, 5 days" are not.

    Adapted from django.utils.timesince
    """
    chunks = (
      (60 * 60 * 24 * 365, lambda n: ungettext('year', 'years', n)),
      (60 * 60 * 24 * 30, lambda n: ungettext('month', 'months', n)),
      (60 * 60 * 24 * 7, lambda n : ungettext('week', 'weeks', n)),
      (60 * 60 * 24, lambda n : ungettext('day', 'days', n)),
      (60 * 60, lambda n: ungettext('hour', 'hours', n)),
      (60, lambda n: ungettext('minute', 'minutes', n)),
      (1, lambda n: ungettext('second', 'seconds', n))
    )
    if duration <= 0:
        # d is in the future compared to now, stop processing.
        return u'0 ' + ugettext('seconds')
    for i, (seconds, name) in enumerate(chunks):
        count = duration // seconds
        if count != 0:
            break
    s = ugettext('%(number)d %(type)s') % {'number': count, 'type': name(count)}
    if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (duration - (seconds * count)) // seconds2
        if count2 != 0:
            s += ugettext(', %(number)d %(type)s') % {'number': count2, 'type': name2(count2)}
    return s
