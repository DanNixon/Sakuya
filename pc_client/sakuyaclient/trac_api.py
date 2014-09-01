import urllib
from bs4 import BeautifulSoup

class TracAPI(object):

    def __init__(self, trac_url):
        self._url = trac_url + '/query'

    def get_query(self, cols=None, owner=None, status=None, order='Priority'):
        # Can't do a query with no columns
        if cols is None:
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

        str_data = urllib.urlopen(url).read()
        document = BeautifulSoup(str_data)
        return document
