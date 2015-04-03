import sys
import time
from sakuyaclient.NotificationSink import NotificationSink


class ConsoleSink(NotificationSink):
    """
    Used to print updates to stdout.
    """


    def __init__(self, config):
        self._verbose = config['verbose'] == 'True'
        self._jenkins_url_pattern = config.get('jenkins_url_pattern', None)
        self._trac_url_pattern = config.get('trac_url_pattern', None)
        self._timestamp_format = config.get('timestamp_format', None)


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


    def _print_timestamp(self):
        """
        Prints a timestamp acording to the format in the timestamp_format option.
        """
        if self._timestamp_format is not None:
            timestamp = time.strftime(self._timestamp_format)
            sys.stdout.write('%s: ' % timestamp)


    def _handle_jenkins(self, job):
        """
        Handles printing a Jenkins build.
        """
        self._print_timestamp()

        if 'last_result' in job:
            if not job['inprogress']:
                sys.stdout.write('Build %s went from %s to %s\n' %
                        (job['name'], job['last_result'], job['result']))
            else:
                sys.stdout.write('Build %s started (previously %s)\n' %
                        (job['name'], job['last_result']))
        else:
            sys.stdout.write('Build %s is %s\n' %
                    (job['name'], job['result']))

        if self._jenkins_url_pattern is not None:
            url = self._jenkins_url_pattern % job['name']
            sys.stdout.write('\t(%s)\n' % url)


    def _handle_trac(self, ticket):
        """
        Handles printing a Trac ticket.
        """
        self._print_timestamp()

        if 'last_status' in ticket:
            sys.stdout.write('Ticket %s went from %s to %s: %s\n' %
                    (ticket['id'], ticket['last_status'], ticket['status'], ticket['summary']))
        else:
            sys.stdout.write('Ticket %s is %s: %s\n' %
                    (ticket['id'], ticket['status'], ticket['summary']))

        if self._trac_url_pattern is not None:
            url = self._trac_url_pattern % ticket['id'][1:]
            sys.stdout.write('\t(%s)\n' % url)
