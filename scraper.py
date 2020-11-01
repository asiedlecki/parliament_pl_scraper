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


class DayVotingPage(ParliamentPage):

    def __init__(self, date, *args, **kwargs):
        super(DayVotingPage, self).__init__(*args, **kwargs)
        self.date = date
        self.votes = {}

    def get_dict_of_votes(self):
        table_rows = (self.soup.find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                      .tbody.find_all('tr'))

        for row in table_rows:
            time = row.td.next_sibling.get_text()
            subject = row.td.next_sibling.next_sibling.a.get_text()
            voting_nr = row.a.get_text()
            link = row.a.attrs['href']
            self.votes[time] = {'voting_nr': voting_nr, 'subject': subject, 'link': link}


class SingleVotingPage(ParliamentPage):

    def __init__(self, subject, voting_nr, *args, **kwargs):
        super(SingleVotingPage, self).__init__(*args, **kwargs)
        club_link_regex = '^agent.xsp\?symbol=klubglos'
        self.subject = subject
        self.voting_nr = voting_nr
        self.clubs_list = [(a.get_text(), a.attrs['href']) for a in self.soup.find_all('a')
                           if re.search(club_link_regex, a.attrs['href'])]


class SingleClubVotesPage(ParliamentPage):

    def __init__(self, club, *args, **kwargs):
        super(SingleClubVotesPage, self).__init__(*args, **kwargs)
        club_link_regex = '^agent.xsp\?symbol=klubglos'
        self.club = club
        self.person_vote = self.get_vote_per_person()

    def get_vote_per_person(self):
        cols_with_name = [1, 4]
        persons_dict = {}
        for td in [tr.findAll('td') for tr in self.soup.find('tbody').findAll('tr')]:
            for col in cols_with_name:
                try:
                    persons_dict[td[col].string] = td[col + 1].string
                except IndexError:
                    pass
        return persons_dict