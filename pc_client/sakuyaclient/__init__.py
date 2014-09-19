import argparse
import sys

from notification_centre import NotificationCentre

from tilda_driver import TiLDADriver

from console_sink import ConsoleSink

from jenkins import JenkinsClient
from trac import TracClient


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
        '--baud',
        action='store',
        type=int,
        default=115200,
        help='Specifies serial baud rate'
    )

    parser.add_argument(
        '--tilda-test',
        action='store_true',
        help='Perform a test of the TiLDA MKe and exit'
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

    if props.tilda_test:
        tilda_test(props)
    else:
        start_client(props)


def start_client(props):
    """
    Runs the client application.

    @param props Application properties
    """

    # Create notification manager
    notifications = NotificationCentre(props.interval)

    # Create notification sources
    jenkins = JenkinsClient(props.jenkins_url, props.jenkins_cache, props.builds.split(','))
    trac = TracClient(props.trac_url, props.trac_cache)
    trac.set_subscriptions(props.ticket_owners.split(','))

    # Add notification sources
    notifications.add_notification_source('tickets', trac)
    notifications.add_notification_source('builds', jenkins)

    # Create notification sinks
    console_sink = ConsoleSink(props.verbose)

    # Add notification sinks
    notifications.add_notification_sink('console1', console_sink)

    # Start update loop
    notifications.start()


def tilda_test(props):
    """
    Runs a simple test of the TiLDA.

    @param props Application properties
    """

    tilda = TiLDADriver()
    tilda.connect(props.port, props.baud)

    tilda.set_led(1, 10, 0, 0)
    tilda.set_led(2, 0, 10, 0)

    tilda.send_notification(0, 0, 'Test notif. #1', 'NOW')
    tilda.send_notification(1, 1, 'Test notif. #2', 'NOW')
    tilda.send_notification(2, 2, 'Test notif. #3', 'NOW')
    tilda.send_notification(3, 3, 'Test notif. #4', 'NOW')

    tilda.release()
