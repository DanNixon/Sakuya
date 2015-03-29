import json
from sakuyaclient.NotificationSource import NotificationSource
from sakuyaclient.sources.TracAPI import TracAPI


class TracSource(NotificationSource):
    """
    Used to manage getting notifications of Trac ticket updates.
    """

    def name(self):
        return 'Trac'


    def __init__(self, config):
        self._url = config['url']
        self._api = TracAPI(self._url)

        self._cache_filename = config['cache_filename']

        self._subscription = dict()
        self._subscription['status'] = ['assigned', 'new', 'inprogress', 'verify', 'verifying', 'closed', 'reopened', 'infoneeded']
        self._subscription['owners'] = config['owners'].split(',')
        self._columns = ['id', 'status', 'summary']  # The bare minimun columns needed


    def _write_cache(self, filename, tickets):
        """
        Writes the ticket dictionary to file.
        """
        with open(filename, 'w+') as cache_file:
            json.dump(tickets, cache_file)


    def _read_cache(self, filename):
        """
        Reads the ticket dictionary from file.
        """
        try:
            with open(filename, 'r') as cache_file:
                tickets = json.load(cache_file)
                return tickets
        except IOError:
            return []


    def _diff(self, old, new):
        """
        Compares two ticket dictionaries and returns the changed tickets.
        """
        changed_tickets = list()

        for ticket in new:
            ticket_id = ticket['id']

            try:
                old_ticket = (t for t in old if t['id'] == ticket_id).next()
            except StopIteration:
                old_ticket = None

            if old_ticket is None:
                changed_tickets.append(ticket)
                continue

            if ticket['status'] != old_ticket['status']:
                ticket['last_status'] = old_ticket['status']
                changed_tickets.append(ticket)
                continue

        return changed_tickets


    def set_data_columns(self, columns):
        """
        Set the columns that are retrieved from the Trac query.
        """
        if len(columns) == 0:
            raise ValueError('Must be at least one columns')

        if not 'id' in columns:
            columns.append('id')

        if not 'status' in columns:
            columns.append('status')

        self._columns = columns


    def poll(self):
        """
        Gets new ticket data and compares it to the last retrieved.
        """
        old_tickets = self._read_cache(self._cache_filename)
        new_tickets = self._api.get_query(self._columns, self._subscription['owners'], self._subscription['status'])

        diff_tickets = self._diff(old_tickets, new_tickets)

        self._write_cache(self._cache_filename, new_tickets)

        return diff_tickets
