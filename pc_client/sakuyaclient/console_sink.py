import sys
from notification_sink import NotificationSink

class ConsoleSink(NotificationSink):

    def handle(self, updates):
        for source in updates.keys():
            sys.stdout.write('Updates from ' + source + '\n')
            for update in updates[source]:
                print update
