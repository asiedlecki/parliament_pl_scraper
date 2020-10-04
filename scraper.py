from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError
import re

class ParliamentPage():

    def __init__(self, uri):
        self.host = 'http://www.sejm.gov.pl/Sejm9.nsf'
        self.uri = uri
        self.read_page()
        self.make_soup()

    def read_page(self):
        try:
            url = '{0}/{1}'.format(self.host, self.uri)
            print(url)
            self.html = urlopen(url).read()
        except HTTPError as e:
            print(e)
        except URLError as e:
            print('The server could not be found!')

    def make_soup(self):
        try:
            self.soup = BeautifulSoup(self.html, 'html.parser')
        except AttributeError as e:
            print(e)


class MainVotingPage(ParliamentPage):

    def get_dict_of_days(self):
        table_rows = (self.soup.find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                      .tbody.find_all('tr'))

        self.days_dict = {}
        for row in table_rows:
            if row.td.get_text().strip() != "":
                session = row.td.get_text()
            date = row.a.get_text()
            votings = row.find('td', {'class': 'right'}).get_text()
            link = row.a.attrs['href']
            self.days_dict[date] = {'session': session, 'votings': votings, 'link': link}