# Parliament PL Scraper
Parliament PL scraper is a Python app for scraping results of votings of Polish parliament.

# Usage examples
(when ran in main repo directory)

## 1. Set up environment

- clone repository
    ```bash
    $ git clone https://github.com/asiedlecki/parliament_pl_scraper.git
    ```
    ```bash
    $ cd parliament_pl_scraper
    ```
- execute following to install all dependencies
    ```bash
    $ pipenv install
    $ pipenv shell
    ```

## 2. Run Jupyter notebook within environment

```bash
$ pipenv run jupyter notebook
```

## 3. Run scraper
#### In Jupyter Notebook:
```python
# tell Python about that additional module import path
import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
# add configuration
sys.path.append(module_path)

import src.dataproc as dp

# run scraping (for single day)
scraped_data = dp.batch_dump_parliament_votings(term=9, dates=['2019-11-12'])

# run batch scraping (for all dates in 'dates')
scraped_data = dp.batch_dump_parliament_votings(term=9, dates=['2019-11-12', '2019-11-13'])

# run batch scraping (for all dates of given term)
scraped_data = dp.batch_dump_parliament_votings(term=9)
```

## 4. Insert scraped data into MongoDB
#### Run docker containers with MongoDB and Mongo Express in terminal.
```bash
$ docker-compose up
```

#### Initiate MongoDB client in Jupyter Notebook and insert data.
```python
# set up Mongo client
client = dp.MyMongoClient()
client.set_votes_collection()
client.db.coll.insert_many(documents=scraped_data, ordered=False)
```
#### Check what has been inserted.
```python
# number of records (documents)
client.db.coll.estimated_document_count()

# what days are inserted
client.db.coll.find({}, {'date': 1}).distinct('date')
```
# Running unit tests

```bash
$ pipenv shell
$ python -m test.tests
```