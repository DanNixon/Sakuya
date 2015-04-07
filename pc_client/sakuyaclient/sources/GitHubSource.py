import github3
from sakuyaclient.NotificationSource import NotificationSource


class GitHubSource(NotificationSource):
    """
    Used to manage getting notifications from GitHub
    """

    def name(self):
        return 'GitHub'


    def __init__(self, config):
        token = config['oauth_token']
        self._github = github3.GitHub()
        self._github.login(token=token)


    def poll(self):
        """
        Gets notifications from GiHub.
        """

        notifications = list()

        gh_notifs = self._github.notifications()
        for notif in gh_notifs:
            parsed_notif = dict()
            parsed_notif['title'] = notif.subject['title']
            parsed_notif['type'] = notif.subject['type']

            notifications.append(parsed_notif)

        return notifications
