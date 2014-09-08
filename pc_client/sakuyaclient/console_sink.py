import sys
from notification_sink import NotificationSink

class ConsoleSink(NotificationSink):
    """
    Used to print updates to stdout.
    """

    def __init__(self, verbose):
        self._verbose = verbose

    def handle(self, updates):
        """
        Handle the new notifications.
        """
        for source in updates.keys():
            update_type = updates[source][0]
            source_updates = updates[source][1]

            if len(source_updates) == 0:
                if self._verbose:
                    sys.stdout.write('No updates from %s\n' % source)
                continue

            for update in source_updates:
                if update_type == 'Jenkins':
                    self._handle_jenkins(update)

                if update_type == 'Trac':
                    self._handle_trac(update)

            sys.stdout.write('----------\n')

    def _handle_jenkins(self, job):
        """
        Handles printing a Jenkins build.
        """
        if 'last_result' in job:
            sys.stdout.write('Build %s went from %s to %s\n' %
                    (job['name'], job['last_result'], job['result']))
        else:
            sys.stdout.write('Build %s is %s\n' %
                    (job['name'], job['result']))

    def _handle_trac(self, ticket):
        """
        Handles printing a Trac ticket.
        """
        if 'last_status' in ticket:
            sys.stdout.write('Ticket %s went from %s to %s: %s\n' %
                    (ticket['id'], ticket['last_status'], ticket['status'], ticket['summary']))
        else:
            sys.stdout.write('Ticket %s is %s: %s\n' %
                    (ticket['id'], ticket['status'], ticket['summary']))
