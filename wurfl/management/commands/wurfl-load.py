from django.core.management.base import CommandError
from django.core.management.base import BaseCommand

from wurfl import update

class Command(BaseCommand):
    args = '<wurfl_file.xml>'
    help = 'Read and parse a WURLF file to store in the database'
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("This command takes exactly one argument")

        try:
            f = open(args[0], 'r')
            u = update.wurfl(f)
            f.close()

            print '-- %s Update --' % u.get_update_type_display()
            print u.summary
        except Exception, e:
            if options.get('traceback', False):
                import traceback
                traceback.print_exc()
            else:
                raise CommandError(e)
