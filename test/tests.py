import unittest
from urllib.request import urlopen, http
from datetime import datetime
import re
import random

from bs4 import BeautifulSoup

from src.dataproc import batch_dump_parliament_votings
import src.scraper as sc


class TestMainVotingPage(unittest.TestCase):
    bs_main_voting_page = None
    def setUpClass():
        url = 'http://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=posglos&NrKadencji=9'
        TestMainVotingPage.bs_main_voting_page = BeautifulSoup(urlopen(url), 'html.parser')

    def test_web_title_text(self):
        pageTitle = TestMainVotingPage.bs_main_voting_page.find('h1').get_text()
        self.assertEqual('Głosowania na posiedzeniach Sejmu', pageTitle);

    def test_web_list_of_voting_days(self):
        table_of_voting_days = (TestMainVotingPage.bs_main_voting_page
                                .find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                                .tbody.find_all('tr'))
        self.assertIsNotNone(table_of_voting_days, "There is no table on main page")
        self.assertTrue(len(table_of_voting_days) > 0, "There is no data in the table")

    def test_scrap_main_voting_page(self):
        term = 9
        main_voting_page = sc.MainVotingPage(term=term, suffix_uri='agent.xsp?symbol=posglos&NrKadencji={0}'.format(term))
        main_voting_page.get_dict_of_days()
        self.assertIsInstance(main_voting_page.days_dict, dict)
        # get latest date
        latest_date = sorted(list(main_voting_page.days_dict.keys()))[-1]
        self.assertIsInstance(main_voting_page.days_dict[latest_date], dict)
        self.assertEqual(set(main_voting_page.days_dict[latest_date].keys()), {'session', 'link', 'votings'})


class TestDayVotingPage(unittest.TestCase):
    bs_day_voting_page = None
    def setUpClass():
        term=9
        main_url = 'http://www.sejm.gov.pl/Sejm9.nsf/'
        # for testing scraper
        TestDayVotingPage.main_voting_page = sc.MainVotingPage(term=term, suffix_uri='agent.xsp?symbol=posglos&NrKadencji={0}'.format(term))
        TestDayVotingPage.main_voting_page.get_dict_of_days()
        latest_date = sorted(list(TestDayVotingPage.main_voting_page.days_dict.keys()))[-1]
        TestDayVotingPage.latest_data = TestDayVotingPage.main_voting_page.days_dict[latest_date]
        TestDayVotingPage.day_voting_page = sc.DayVotingPage(suffix_uri=TestDayVotingPage.latest_data['link'], date=latest_date)
        TestDayVotingPage.day_voting_page.get_dict_of_votes()
        # for testing structure of website
        TestDayVotingPage.bs_day_voting_page = BeautifulSoup(urlopen(main_url+TestDayVotingPage.latest_data['link']), 'html.parser')

    def test_title_text(self):
        pageTitle = TestDayVotingPage.bs_day_voting_page.find('h1').get_text()
        self.assertEqual('Głosowania w dniu', pageTitle[:17]);

    def test_list_of_voting_days(self):
        table_of_voting_days = (TestDayVotingPage.bs_day_voting_page
                                .find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                                .tbody.find_all('tr'))
        self.assertIsNotNone(table_of_voting_days, "There is no table on main page")
        self.assertTrue(len(table_of_voting_days) > 0, "There is no data in the table")

    def test_scrap_day_voting_page(self):
        # self.votes[time] = {'voting_nr': voting_nr, 'subject': subject, 'routine': routine, 'link': link}
        self.assertIsInstance(TestDayVotingPage.day_voting_page.votes, dict)
        latest_time = sorted(list(TestDayVotingPage.day_voting_page.votes.keys()))[-1]
        self.assertIsInstance(TestDayVotingPage.day_voting_page.votes[latest_time], dict)
        self.assertEqual(set(TestDayVotingPage.day_voting_page.votes[latest_time].keys()), {'voting_nr', 'subject', 'routine', 'link'})


class TestVotingPage(unittest.TestCase):
    bs_voting_page = None
    def setUpClass():
        # for testing structure of website
        url = 'http://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=glosowania&NrKadencji=9&NrPosiedzenia=17&NrGlosowania=1'
        TestVotingPage.bs_voting_page = BeautifulSoup(urlopen(url), 'html.parser')
        # for testing scraper
        TestDayVotingPage.main_voting_page = sc.MainVotingPage(uri='agent.xsp?symbol=posglos&NrKadencji=9')
        TestDayVotingPage.main_voting_page.get_dict_of_days()
        latest_date = sorted(list(TestDayVotingPage.main_voting_page.days_dict.keys()))[-1]
        TestDayVotingPage.latest_data = TestDayVotingPage.main_voting_page.days_dict[latest_date]
        TestDayVotingPage.day_voting_page = sc.DayVotingPage(uri=TestDayVotingPage.latest_data['link'],
                                                             date=latest_date)
        TestDayVotingPage.day_voting_page.get_dict_of_votes()

    def test_title_text(self):
        pageTitle = TestVotingPage.bs_voting_page.find('h1').get_text()
        self.assertEqual('Głosowanie nr', pageTitle[:13]);

    def test_links_to_clubs_exist(self):
        club_link_regex = '^agent.xsp\?symbol=klubglos'
        clubs_list = [(a.get_text(), a.attrs['href']) for a in TestVotingPage.bs_voting_page.find_all('a')
                      if re.search(club_link_regex, a.attrs['href'])]
        self.assertTrue(len(clubs_list) > 0, "There is no link to club votes")


class TestClubVotesPage(unittest.TestCase):
    bs_club_page = None
    def setUpClass():
        url = 'http://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=klubglos&IdGlosowania=53923&KodKlubu=Konfederacja'
        TestClubVotesPage.bs_club_page = BeautifulSoup(urlopen(url), 'html.parser')

    def test_title_text(self):
        pageTitle = (TestClubVotesPage.bs_club_page
                     .find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                     .find('h1').get_text())
        self.assertEqual('Wyniki imienne posłów', pageTitle[:21]);

    def test_get_proper_votes(self):
        cols_with_name = [1, 4]

        person_vote = {}
        for td in [tr.findAll('td') for tr in TestClubVotesPage.bs_club_page.find('tbody').findAll('tr')]:
            for col in cols_with_name:
                try:
                    person_vote[td[col].string] = td[col + 1].string
                except IndexError:
                    pass

        self.assertTrue(len(set(person_vote.keys())) >= 3, "Less than 3 persons within the club")
        self.assertEqual({'Wstrzymał się', 'Nieobecny', 'Przeciw', 'Za'}, set(person_vote.values()))

class TestVotingsBatchDump(unittest.TestCase):
    def setUpClass():
        TestVotingsBatchDump.output = batch_dump_parliament_votings(term=9, votings_threshold=2)
        TestVotingsBatchDump.votes_values = set(dict_['vote'] for dict_ in TestVotingsBatchDump.output)

    def test_data_types(self):
        self.assertIsInstance(TestVotingsBatchDump.output, list)
        self.assertIsInstance(TestVotingsBatchDump.output[-1], dict)

    def test_number_of_fields(self):
        self.assertTrue(len(TestVotingsBatchDump.output[-1]) == 11)

    def test_key_data(self):
        self.assertEqual(TestVotingsBatchDump.votes_values, {'Za', 'Przeciw', 'Wstrzymał się', 'Nieobecny'}) # votes
        self.assertTrue(min((len(value.split(' ')) for value
                             in TestVotingsBatchDump.gather_field_values(self, field_name='person'))) == 2) # names
        self.assertEqual({type(int(value)) for value
                               in TestVotingsBatchDump.gather_field_values(self, field_name='session')}, {int})  # sessions
        self.assertTrue(min({int(value) for value
                             in TestVotingsBatchDump.gather_field_values(self, field_name='votings')}) >= 1)  # votings
        self.assertTrue(min({len(value) for value
                        in TestVotingsBatchDump.gather_field_values(self, field_name='club')}) == 2)  # club names min
        self.assertIsInstance([datetime.strptime(dt, '%Y-%m-%d') for dt
                               in TestVotingsBatchDump.gather_field_values(self, field_name='date')][0], datetime) # date

    def gather_field_values(self, field_name):
        return set(dict_[field_name] for dict_ in TestVotingsBatchDump.output)


if __name__ == '__main__':
    unittest.main(warnings='ignore')