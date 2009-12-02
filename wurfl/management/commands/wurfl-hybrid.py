from django.core.management.base import NoArgsCommand
from wurfl import update
from wurfl.models import Update

class Command(NoArgsCommand):
    help = 'Build the hybrid table from the available patches and devices.'
    
    def handle_noargs(self, *args, **options):
        print 'Building hybrid tables from patches and original devices...'
        updates = update.hybrid()
            
        for u in updates:
            print '-- %s Update --' % u.get_update_type_display()
            print u.summary
