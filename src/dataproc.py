import math
from typing import Union
import json
from datetime import datetime

from pymongo import MongoClient

from src import scraper as sc


def batch_dump_parliament_votings(term:int=9, dates:Union[list, set]=[],
                                  votings_threshold:Union[int, float]=math.inf,
                                  dates_to_ignore:Union[list, set]=None,
                                  insert_to_db:bool=False) -> list:
    assert isinstance(dates_to_ignore, (list, set)) or dates_to_ignore is None, \
        f"days_to_ignore should be of type (list, set), yet is of type {type(dates_to_ignore)}"

    uri = 'agent.xsp?symbol=posglos&NrKadencji={t}'.format(t=term)
    records_list = []
    main_voting_page = sc.MainVotingPage(term=term, suffix_uri=uri)
    main_voting_page.get_dict_of_days()

    if len(dates) > 0:
        dates_to_scrape = {key:value for key, value in main_voting_page.days_dict.items() if key in dates}
    if dates_to_ignore:
        for day in dates_to_ignore:
            dates_to_scrape.pop(day, None)

    for day, day_values in dates_to_scrape.items():
        day_records = []
        print(datetime.now(), '---', day, '--- start')
        parse_by_date_bool = (day in dates) | (len(dates) == 0)
        parse_by_votings_threshold_bool = int(day_values['votings']) < votings_threshold

        if parse_by_date_bool & parse_by_votings_threshold_bool:
            day_page = sc.DayVotingPage(term=term, suffix_uri=day_values['link'],
                                        date=day)
            day_page.get_dict_of_votes()

            for voting, voting_values in day_page.votes.items():
                voting_page = sc.SingleVotingPage(term=term,
                                                  suffix_uri=voting_values['link'],
                                                  subject=voting_values['subject'],
                                                  voting_nr=voting_values['voting_nr']
                                                  )

                for club in voting_page.clubs_list:
                    club_page = sc.SingleClubVotesPage(term=term,
                                                       suffix_uri=club[1],
                                                       club=club[0])
                    club_page.get_vote_per_person()

                    for person, person_vote in club_page.person_vote.items():
                        day_records.append({'date': day, 'session': day_values['session'],
                                            'votings': day_values['votings'], 'time': voting,
                                            'subject': voting_values['subject'], 'routine': voting_values['routine'],
                                            'voting_nr': voting_values['voting_nr'], 'club': club[0],
                                            'person': person, 'vote': person_vote,
                                            'inserted_dt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        if insert_to_db:
            if 'client' not in locals():
                client = MyMongoClient()
                client.set_votes_collection()
            client.db.coll.insert_many(documents=day_records, ordered=False)
            print(datetime.now(), '---', day, '--- scraped & inserted')
        else:
            print(datetime.now(), '---', day, '--- scraped')
        records_list.extend(day_records)

    return records_list


class Configuration():
    def __init__(self):
        with open('configuration/configuration_prod.json') as f:
            self.config = json.load(f)


class MyMongoClient(MongoClient):
    def __init__(self, *args, **kwargs):
        super(MyMongoClient, self).__init__(*args, **kwargs)

    def set_votes_collection(self):
        db_name = Configuration().config['mongodb']['parliament_votes']['database']
        self.db = self[db_name]
        coll_name = Configuration().config['mongodb']['parliament_votes']['collection']
        self.coll = self.db[coll_name]