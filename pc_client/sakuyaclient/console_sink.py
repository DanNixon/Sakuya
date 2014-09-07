import sys
from notification_sink import NotificationSink

class ConsoleSink(NotificationSink):

    def handle(self, updates):
        for source in updates.keys():
            update_type = updates[source][0]

            for update in updates[source][1]:
                if update_type == 'Jenkins':
                    if 'last_result' in update:
                        sys.stdout.write('Build %s went from %s to %s\n' %
                                (update['name'], update['result'], update['last_result']))
                    else:
                        sys.stdout.write('Build %s is %s\n' %
                                (update['name'], update['result']))

                if update_type == 'Trac':
                    if 'last_status' in update:
                        sys.stdout.write('Ticket %s went from %s to %s: %s\n' %
                                (update['id'], update['status'], update['last_status'], update['summary']))
                    else:
                        sys.stdout.write('Ticket %s is %s: %s\n' %
                                (update['id'], update['status'], update['summary']))
