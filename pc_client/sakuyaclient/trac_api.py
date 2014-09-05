import urllib
from bs4 import BeautifulSoup

class TracAPI(object):
    """
    Basic API to access Trac via HTML scraping.
    """

    def __init__(self, trac_url):
        self._url = trac_url + '/query'

    def get_query(self, cols=None, owner=None, status=None, order='Priority'):
        """
        Gets a list of tickets for a given query.
        """
        url = self._get_url(cols, owner, status, order)

        str_data = urllib.urlopen(url).read()
        document = BeautifulSoup(str_data)

        tickets = self._parse_document(document)

        return tickets

    def _get_url(self, cols, owner, status, order):
        """
        Creates a URL for given query parameters.
        """
        # Can't do a query with no columns
        if cols is None or len(cols) is 0:
            raise RuntimeError

        url = self._url + '?order=' + order

        # Add columns
        for col_name in cols:
            url += '&col=' + col_name

        # Add owner filters
        if owner is not None:
            for owner_name in owner:
                url += '&owner=' + owner_name

        # Add status filters
        if status is not None:
            for status_type in status:
                url += '&status=' + status_type

        return url

    def _parse_document(self, document):
        """
        Parses a HTML document and extracts ticket information.
        """
        tickets = list()
        headers = list()

        # Get all table rows in tickets table
        for table_row in document.select('.tickets')[0].findAll('tr'):
            ticket_data = dict()

            # Get all data cells in table
            for table_data in table_row.findAll('td'):
                key = table_data['class'][0]
                try:
                    value = table_data.string.strip()
                except AttributeError:
                    value = table_data.a.string.strip()

                ticket_data[key] = value

            # Append only if data exists
            if len(ticket_data) > 0:
                tickets.append(ticket_data)

        return tickets
