# Parliament PL Scraper
Parliament PL scraper is a Python app for scraping results of votings of Polish parliament.

# Usage examples
(when ran in main repo directory)

## 1. Set up environment

- clone repository
- in main directory execute following to install all dependencies
```python
pipenv install
pipenv shell
```

## 2. Run Jupyter notebook within environment

```python
pipenv run jupyter notebook
```

## 3. Run scraper

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

# run batch scraping (for single day)
scraped_data = dp.batch_dump_parliament_votings(term=9, dates=['2019-11-12'])

# run batch scraping (for all dates in 'dates')
scraped_data = dp.batch_dump_parliament_votings(term=9, dates=['2019-11-12', '2019-11-13'])

# run batch scraping (for all dates of given term)
scraped_data = dp.batch_dump_parliament_votings(term=9)
```

## 4. Insert scraped data into MongoDB
This tutorial assumes that a MongoDB instance is running on the default host and port.
- If you need to download and install MongoDB, follow tutorial:
https://docs.mongodb.com/manual/installation/
- Assuming you have downloaded and installed MongoDB, you can start it in terminal like so:
```bash
$ mongod
```

```python
# set up Mongo client
client = dp.MyMongoClient()
client.set_votes_collection()
client.db.coll.insert_many(documents=scraped_data, ordered=False)
```
# Running tests

```python
pipenv shell
python -m test.tests
```