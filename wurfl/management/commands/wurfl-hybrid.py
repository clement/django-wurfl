from django.core.management.base import NoArgsCommand
from wurfl import update

class Command(NoArgsCommand):
    help = 'Build the hybrid table from the available patches and devices.'
    
    def handle_noargs(self, *args, **options):
        try:
            print 'Building hybrid tables from patches and original devices...'
            update.hybrid()
            print 'Hybrid table built successfully.'
        except Exception, e:
            print e.message
