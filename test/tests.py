import unittest
from urllib.request import urlopen, http
from bs4 import BeautifulSoup

class TestMainVotingPage(unittest.TestCase):
    bs_main_voting_page = None
    def setUpClass():
        url = 'http://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=posglos&NrKadencji=9'
        TestMainVotingPage.bs_main_voting_page = BeautifulSoup(urlopen(url), 'html.parser')

    def test_title_ext(self):
        pageTitle = TestMainVotingPage.bs_main_voting_page.find('h1').get_text()
        self.assertEqual('Głosowania na posiedzeniach Sejmu', pageTitle);

    def test_list_of_voting_days(self):
        table_of_voting_days = (TestMainVotingPage.bs_main_voting_page
                                .find('div', {'id': 'view:_id1:_id2:facetMain:agentHTML'})
                                .tbody.find_all('tr'))
        self.assertIsNotNone(table_of_voting_days, "There is no table on main page")
        self.assertTrue(len(table_of_voting_days) > 0, "There is no data in the table")

if __name__ == '__main__':
    unittest.main(warnings='ignore')