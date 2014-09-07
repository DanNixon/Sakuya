import argparse
import sys

from jenkins import JenkinsClient
from trac import TracClient
from notification_centre import NotificationCentre
from console_sink import ConsoleSink

def run():
    sys.stdout.write('Help me Eirin!\n')
    console_test()

def console_test():
    trac_cache_file = 'ticket_cache.txt'
    builds_cache_file = 'builds_cache.txt'
    builds = ['develop_clean', 'develop_incremental', 'pylint_develop']

    jenkins = JenkinsClient('http://builds.mantidproject.org', builds_cache_file, builds)
    trac = TracClient('http://trac.mantidproject.org/mantid', trac_cache_file)
    trac.set_subscriptions(['Dan Nixon'])

    notifications = NotificationCentre(60)

    notifications.add_notification_source('tickets', trac)
    notifications.add_notification_source('builds', jenkins)

    notification_sink = ConsoleSink()

    notifications.add_notification_sink('console1', notification_sink)

    notifications.start()
