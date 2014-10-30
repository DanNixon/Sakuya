from time import gmtime, strftime
from enum import Enum
from sakuyaclient.notification_sink import NotificationSink
from sakuyaclient.tilda_driver import NotificationTypes, Bitmaps


class State(Enum):
    WORST = 0
    BAD = 1
    NEUTRAL = 2
    GOOD = 3
    BEST = 4


class TiLDASink(NotificationSink):
    """
    Manages notification for the TiLDA MKe.
    """

    def __init__(self, tilda_driver, jenkins_user):
        self._tilda = tilda_driver
        self._jenkins_user = jenkins_user

    def handle(self, updates):
        """
        Handle the new notifications.
        """

        jenkins_led_state = State.NEUTRAL
        trac_led_state = State.NEUTRAL

        update_count = {'Jenkins':0, 'Trac':0}

        for source in updates.keys():
            update_type = updates[source][0]
            source_updates = updates[source][1]

            if len(source_updates) == 0:
                continue

            for update in source_updates:
                update_count[update_type] += 1

                if update_type == 'Jenkins':
                    state = self._handle_jenkins(update)
                    if state.value < jenkins_led_state.value:
                        jenkins_led_state = state
                    if state.value > jenkins_led_state.value and jenkins_led_state.value >= State.NEUTRAL.value:
                        jenkins_led_state = state

                if update_type == 'Trac':
                    state = self._handle_trac(update)
                    if state.value < trac_led_state.value:
                        trac_led_state = state
                    if state.value > trac_led_state.value and trac_led_state.value >= State.NEUTRAL.value:
                        trac_led_state = state

        if update_count['Jenkins'] > 0:
            self._set_led(1, jenkins_led_state)
        if update_count['Trac'] > 0:
            self._set_led(2, trac_led_state)

    def _handle_jenkins(self, job):
        """
        Handles giving Jenkins notifications.
        """

        notif_time = strftime("%H:%M", gmtime())

        # Ignore jobs that are in progress
        if job['inprogress']:
            return State.NEUTRAL

        job_name = job['name']
        result = job['result']

        state = State.NEUTRAL

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
                state = State.WORST
            if change == 'broken' and was_me == '':
                notif_bitmap = Bitmaps.PATCHY_2
                state = State.BAD
            if change == 'fixed':
                notif_bitmap = Bitmaps.PATCHY_1
                state = State.BEST
            if change == 'slightly broken':
                notif_bitmap = Bitmaps.SAKUYA_2
                state = State.BAD
            if change == 'somewhat fixed':
                notif_bitmap = Bitmaps.SAKUYA_2
                state = State.GOOD

            notif_desc = '%s was %s %s' % (job_name, change, was_me)

        self._tilda.send_notification(NotificationTypes.BUILD.value, notif_bitmap.value, notif_desc, notif_time)
        return state

    def _what_happened_to_the_build(self, result, old_result):
        """
        Determines in what way a build was broken (or fixed).
        """

        state_change = 'Master Sparked'

        if result == 'failure' and old_result != 'failure':
            state_change = 'broken'

        if result == 'unstable' and old_result == 'failure':
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

        state = State.NEUTRAL

        if status == 'new' or status == 'assigned':
            notif_bitmap = Bitmaps.YUUKA
            notif_desc = '%s is a new ticket' % (ticket_no)

        if status == 'inprogress':
            notif_bitmap = Bitmaps.NITORI
            notif_desc = '%s is in progress' % (ticket_no)

        if status == 'verifying':
            state = State.GOOD
            notif_bitmap = Bitmaps.KOMACHI
            notif_desc = '%s is being verified' % ticket_no

        if status == 'reopened':
            state = State.WORST
            notif_bitmap = Bitmaps.SHIKI_2
            notif_desc = '%s was reopened' % ticket_no

        if status == 'closed':
            state = State.BEST
            notif_bitmap = Bitmaps.SHIKI_1
            notif_desc = '%s was closed' % ticket_no

        self._tilda.send_notification(NotificationTypes.TICKET.value, notif_bitmap.value, notif_desc, notif_time)
        return state

    def _set_led(self, led_id, state):
        """
        Sets the LEDs such that they represent the worst notification sent in an update.
        """

        if state == State.WORST:
            self._tilda.set_led(led_id, 4, 0, 0)

        if state == State.BAD:
            self._tilda.set_led(led_id, 4, 2, 0)

        if state == State.NEUTRAL:
            self._tilda.set_led(led_id, 2, 2, 0)

        if state == State.GOOD:
            self._tilda.set_led(led_id, 0, 4, 2)

        if state == State.BEST:
            self._tilda.set_led(led_id, 0, 4, 0)
