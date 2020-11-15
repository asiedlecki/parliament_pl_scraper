from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
import re
import json
from datetime import datetime

from bs4 import BeautifulSoup


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
        with open('../configuration/exclusions.json') as f:
            self.days_excluded = list(json.load(f).keys())
        table_rows = (self.soup.find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                      .tbody.find_all('tr'))

        self.days_dict = {}
        for row in table_rows:
            if row.td.get_text().strip() != "":
                session = row.td.get_text()
            date = self.normalize_date(row.a.get_text())
            if date in self.days_excluded: # skip if date is in exclusions list
                continue
            votings = row.find('td', {'class': 'right'}).get_text()
            link = row.a.attrs['href']
            self.days_dict[date] = {'session': session, 'votings': votings, 'link': link}

    def normalize_date(self, date_str: str):
        months_dict = {'stycznia': 1, 'lutego': 2, 'marca': 3,
                       'kwietnia': 4, 'maja': 5, 'czerwca': 6,
                       'lipca': 7, 'sierpnia': 8, 'września': 9,
                       'października': 10, 'listopada': 11, 'grudnia': 12
                       }

        date_str_splitted = date_str.split(sep=' ', maxsplit=2)
        _day = int(date_str_splitted[0])
        _month = months_dict[date_str_splitted[1]]
        _year = int(date_str_splitted[2][:4])

        return datetime(year=_year, month=_month, day=_day).strftime('%Y-%m-%d')


class DayVotingPage(ParliamentPage):

    def __init__(self, date, *args, **kwargs):
        super(DayVotingPage, self).__init__(*args, **kwargs)
        self.date = date
        self.votes = {}

    def get_dict_of_votes(self):
        table_rows = (self.soup.find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                      .tbody.find_all('tr'))
        non_routine_regex = 'Pkt \d{1,4}. porz. dzien.'

        for row in table_rows:
            time = row.td.next_sibling.get_text()
            subject = row.td.next_sibling.next_sibling.get_text()
            routine = not re.search(non_routine_regex, subject)
            voting_nr = row.a.get_text()
            link = row.a.attrs['href']
            self.votes[time] = {'voting_nr': voting_nr, 'subject': subject, 'routine': routine, 'link': link}


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