from time import gmtime, strftime
from notification_sink import NotificationSink
from tilda_driver import NotificationTypes, Bitmaps


class TiLDASink(NotificationSink):
    """
    Manages notification for the TiLDAMKe.
    """

    def __init__(self, tilda_driver, jenkins_user):
        self._tilda = tilda_driver
        self._jenkins_user = jenkins_user

    def handle(self, updates):
        """
        Handle the new notifications.
        """

        for source in updates.keys():
            update_type = updates[source][0]
            source_updates = updates[source][1]

            if len(source_updates) == 0:
                continue

            for update in source_updates:
                if update_type == 'Jenkins':
                    self._handle_jenkins(update)

                if update_type == 'Trac':
                    self._handle_trac(update)

    def _handle_jenkins(self, job):
        """
        Handles giving Jenkins notifications.
        """

        notif_time = strftime("%H:%M", gmtime())

        # Ignore jobs that are in progress
        if job['inprogress']:
            return

        job_name = job['name']
        result = job['result']

        if 'last_result' not in job:
            notif_bitmap = Bitmaps.SAKUYA_2
            notif_desc = '%s is %s' % (job_name, result)

        else:
            last_result = job['last_result']

            change = self._what_happened_to_the_build(result, last_result)
            was_me = self._was_that_me(job)

            notif_bitmap = Bitmaps.PATCHY_2

            if change == 'broken' and was_me != '':
                notif_bitmap = Bitmaps.FLAN
            if change == 'broken' and was_me == '':
                notif_bitmap = Bitmaps.PATCHY_2
            if change == 'fixed':
                notif_bitmap = Bitmaps.PATCHY_1
            if change == 'slightly broken':
                notif_bitmap = Bitmaps.SAKUYA_2
            if change == 'somewhat fixed':
                notif_bitmap = Bitmaps.SAKUYA_2

            notif_desc = '%s was %s %s' % (job_name, change, was_me)

        self._tilda.send_notification(NotificationTypes.BUILD.value, notif_bitmap.value, notif_desc, notif_time)

    def _what_happened_to_the_build(self, result, old_result):
        """
        Determines in what way a build was broken (or fixed).
        """

        state_change = 'Master Spark\'ed'

        if result == 'failed' and old_result != 'failed':
            state_change = 'broken'

        if result == 'unstable' and old_result == 'failed':
            state_change = 'somewhat fixed'

        if result == 'success' and old_result != 'success':
            state_change = 'fixed'

        if result == 'unstable' and old_result == 'success':
            state_change = 'slightly broken'

        return state_change

    def _was_that_me(self, job):
        """
        Determines if a change to the build status could have been caused by me.
        """

        if self._jenkins_user in job['culprits']:
            if len(job['culprits']) == 1:
                return 'by me'
            else:
                return 'possibly by me'
        else:
            return ''


    def _handle_trac(self, ticket):
        """
        Handles giving Trac notifications.
        """

        notif_time = strftime("%H:%M", gmtime())

        ticket_no = ticket['id']
        status = ticket['status']

        notif_bitmap = Bitmaps.SAKUYA_1
        notif_desc = '%s is now %s' % (ticket_no, status)

        if status == 'reopened' or status == 'closed':
            notif_bitmap = Bitmaps.SHIKI
            notif_desc = '%s was %s' % (ticket_no, status)

        elif status == 'new' or status == 'assigned':
            notif_bitmap = Bitmaps.YUUKA
            notif_desc = '%s is a new ticket' % (ticket_no)

        self._tilda.send_notification(NotificationTypes.TICKET.value, notif_bitmap.value, notif_desc, notif_time)
