from src import scraper as sc
import math
from datetime import datetime
from typing import Union
from pymongo import MongoClient
import json


def batch_dump_parliament_votings(term:int=9, dates:list=[],
                                  votings_threshold:Union[int, float]=math.inf):
    uri = 'agent.xsp?symbol=posglos&NrKadencji={t}'.format(t=term)
    records_list = []
    main_voting_page = sc.MainVotingPage(uri)
    main_voting_page.get_dict_of_days()

    for day, day_values in main_voting_page.days_dict.items():
        parse_by_date_bool = (normalize_date(day) in dates) | (len(dates) == 0)
        parse_by_votings_threshold_bool = int(day_values['votings']) < votings_threshold
        if parse_by_date_bool & parse_by_votings_threshold_bool:
            day_page = sc.DayVotingPage(uri=day_values['link'],
                                        date=day)
            day_page.get_dict_of_votes()

            for voting, voting_values in day_page.votes.items():
                voting_page = sc.SingleVotingPage(uri=voting_values['link'],
                                                  subject=voting_values['subject'],
                                                  voting_nr=voting_values['voting_nr']
                                                  )

                for club in voting_page.clubs_list:
                    club_page = sc.SingleClubVotesPage(uri=club[1],
                                                    club=club[0])
                    club_page.get_vote_per_person()

                    for person, person_vote in club_page.person_vote.items():
                        records_list.append({'date': normalize_date(day), 'session': day_values['session'],
                                             'votings': day_values['votings'], 'time': voting,
                                             'subject': voting_values['subject'], 'routine': voting_values['routine'],
                                             'voting_nr': voting_values['voting_nr'], 'club': club[0],
                                             'person': person, 'vote': person_vote})

    return records_list


def normalize_date(date_str: str):
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


class Configuration():
    def __init__(self):
        with open('configuration_prod.json') as f:
            self.config = json.load(f)


class MyMongoClient(MongoClient):
    def __init__(self, *args, **kwargs):
        super(MyMongoClient, self).__init__(*args, **kwargs)

    def set_votes_collection(self):
        db_name = Configuration().config['mongodb']['parliament_votes']['database']
        self.db = self[db_name]
        coll_name = Configuration().config['mongodb']['parliament_votes']['collection']
        self.coll = self.db[coll_name]