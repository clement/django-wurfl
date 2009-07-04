from optparse import make_option
from django.core.management.base import CommandError
from django.core.management.base import BaseCommand

from wurfl.models import Patch


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--inactive', action='store_false', dest='active', default=True,
            help='Create an initially inactive patch'),
        make_option('-p', '--priority', action='store', type='int', dest='priority', default=None,
            help='Force the priority of the patch, 0 for maximum priority, otherwise a min priority is calculated and assigned'),
    )
    args = '[<name>] <patch_file.xml>'
    help = 'Create a new WURFL patch from an xml file.'
    
    def handle(self, *args, **options):
        if len(args) == 1:
            file_name = args[0]
            name = file_name
        elif len(args) == 2:
            file_name = args[1]
            name = args[0]
        else:
            raise CommandError("Missing patch filename argument")

        try:
            f = open(file_name, 'r')
            patch_content = f.read()
            f.close()

            if options['priority'] == None:
                # Get max priority + 1
                priority = 1
                for p in Patch.objects.order_by('-priority')[:1]:
                    priority = p.priority + 1
            else:
                priority = options['priority']
                
            p = Patch.objects.create(
                name=name,
                patch=patch_content,
                priority=priority,
                active=options['active'],
            )
            print 'Created patch `%s` with id %d' % (name, p.pk)
        except Exception, e:
            raise CommandError(e)
