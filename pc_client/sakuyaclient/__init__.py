import argparse
import sys

from jenkins import JenkinsClient
from trac import TracClient
from notification_centre import NotificationCentre
from console_sink import ConsoleSink

def run():
    """
    Gets command line options and starts Sakuya client.
    """
    parser = argparse.ArgumentParser(description='Client for Sakuya development aid')

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Increases console verbosity'
    )

    parser.add_argument(
        '-p', '--port',
        action='store',
        help='Specifies serial port to communicate with TiLDA MKe'
    )

    parser.add_argument(
        '-i', '--interval',
        action='store',
        type=float,
        default=300,
        help='Time in seconds between polling sources'
    )

    parser.add_argument(
        '--builds',
        action='store',
        default='develop_incremental,develop_clean,develop_doctest,develop_systemtests_rhel6,develop_systemtests_all,cppcheck_develop,doxygen_develop,valgrind_develop_core_packages',
        help='Comma separated list of build jobs to watch'
    )

    parser.add_argument(
        '--ticket-owners',
        action='store',
        default='Dan Nixon',
        help='Comma separated list of owners of tickets to watch'
    )

    parser.add_argument(
        '--jenkins-url',
        action='store',
        default='http://builds.mantidproject.org',
        help='URL for Jenkins build server'
    )

    parser.add_argument(
        '--trac-url',
        action='store',
        default='http://trac.mantidproject.org/mantid',
        help='URL for Trac ticket server'
    )

    parser.add_argument(
        '--jenkins-cache',
        action='store',
        default='jenkins-cache.txt',
        help='Cache file for Jenkins build information'
    )

    parser.add_argument(
        '--trac-cache',
        action='store',
        default='trac-cache.txt',
        help='Cache file for Trac ticket information'
    )

    props = parser.parse_args()

    start_client(props)

def start_client(props):
    jenkins = JenkinsClient(props.jenkins_url, props.jenkins_cache, props.builds.split(','))
    trac = TracClient(props.trac_url, props.trac_cache)
    trac.set_subscriptions(props.ticket_owners.split(','))

    notifications = NotificationCentre(props.interval)

    notifications.add_notification_source('tickets', trac)
    notifications.add_notification_source('builds', jenkins)

    notification_sink = ConsoleSink(props.verbose)

    notifications.add_notification_sink('console1', notification_sink)

    notifications.start()
