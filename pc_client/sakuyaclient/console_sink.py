import sys
from notification_sink import NotificationSink

class ConsoleSink(NotificationSink):

    def handle(self, updates):
        for source in updates.keys():
            sys.stdout.write('Updates from ' + source + '\n')
            update_type = updates[source][0]

            for update in updates[source][1]:
                if update_type == 'Jenkins':
                    print 'Build:', update
                if update_type == 'Trac':
                    print 'Ticket:', update
