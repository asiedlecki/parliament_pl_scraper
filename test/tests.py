import unittest
from urllib.request import urlopen, http
from bs4 import BeautifulSoup
import re

class TestMainVotingPage(unittest.TestCase):
    bs_main_voting_page = None
    def setUpClass():
        url = 'http://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=posglos&NrKadencji=9'
        TestMainVotingPage.bs_main_voting_page = BeautifulSoup(urlopen(url), 'html.parser')

    def test_title_text(self):
        pageTitle = TestMainVotingPage.bs_main_voting_page.find('h1').get_text()
        self.assertEqual('Głosowania na posiedzeniach Sejmu', pageTitle);

    def test_list_of_voting_days(self):
        table_of_voting_days = (TestMainVotingPage.bs_main_voting_page
                                .find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                                .tbody.find_all('tr'))
        self.assertIsNotNone(table_of_voting_days, "There is no table on main page")
        self.assertTrue(len(table_of_voting_days) > 0, "There is no data in the table")


class TestDayVotingPage(unittest.TestCase):
    bs_day_voting_page = None
    def setUpClass():
        url = 'http://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=listaglos&IdDnia=1802'
        TestDayVotingPage.bs_day_voting_page = BeautifulSoup(urlopen(url), 'html.parser')

    def test_title_text(self):
        pageTitle = TestDayVotingPage.bs_day_voting_page.find('h1').get_text()
        self.assertEqual('Głosowania w dniu', pageTitle[:17]);

    def test_list_of_voting_days(self):
        table_of_voting_days = (TestDayVotingPage.bs_day_voting_page
                                .find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                                .tbody.find_all('tr'))
        self.assertIsNotNone(table_of_voting_days, "There is no table on main page")
        self.assertTrue(len(table_of_voting_days) > 0, "There is no data in the table")


class TestVotingPage(unittest.TestCase):
    bs_voting_page = None
    def setUpClass():
        url = 'http://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=glosowania&NrKadencji=9&NrPosiedzenia=17&NrGlosowania=1'
        TestVotingPage.bs_voting_page = BeautifulSoup(urlopen(url), 'html.parser')

    def test_title_text(self):
        pageTitle = TestVotingPage.bs_voting_page.find('h1').get_text()
        self.assertEqual('Głosowanie nr', pageTitle[:13]);

    def test_links_to_clubs_exist(self):
        club_link_regex = '^agent.xsp\?symbol=klubglos'
        clubs_list = [(a.get_text(), a.attrs['href']) for a in TestVotingPage.bs_voting_page.find_all('a')
                      if re.search(club_link_regex, a.attrs['href'])]
        self.assertTrue(len(clubs_list) > 0, "There is no link to club votes")


class TestClubPage(unittest.TestCase):
    bs_club_page = None
    def setUpClass():
        url = 'http://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=klubglos&IdGlosowania=53923&KodKlubu=Konfederacja'
        TestClubPage.bs_club_page = BeautifulSoup(urlopen(url), 'html.parser')

    def test_title_text(self):
        pageTitle = (TestClubPage.bs_club_page
                     .find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                     .find('h1').get_text())
        self.assertEqual('Wyniki imienne posłów', pageTitle[:21]);

    def test_get_proper_votes(self):
        cols_with_name = [1, 4]

        person_vote = {}
        for td in [tr.findAll('td') for tr in TestClubPage.bs_club_page.find('tbody').findAll('tr')]:
            for col in cols_with_name:
                try:
                    person_vote[td[col].string] = td[col + 1].string
                except IndexError:
                    pass

        self.assertTrue(len(set(person_vote.keys())) >= 3, "Less than 3 persons within the club")
        self.assertEqual({'Wstrzymał się', 'Nieobecny', 'Przeciw', 'Za'}, set(person_vote.values()));


if __name__ == '__main__':
    unittest.main(warnings='ignore')