# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: 'Python 3.9.5 (''env'': venv)'
#     language: python
#     name: python3
# ---

# +
'''
Convert results from sql queries to csv files
'''
import sys

import os 
from os import environ as env

import mysql.connector
from mysql.connector import Error

import pandas as pd

# -

if 'DB_PWD' in os.environ:
    del os.environ['DB_PWD']

from dotenv import load_dotenv
load_dotenv()

# ## Warning!
#
# We should use SQALchemy connection with pandas.
#
# /home/jurra/work/projects/2022-Dyned/repos/dyned/env/lib/python3.9/site-packages/pandas/io/sql.py:761: UserWarning: pandas only support SQLAlchemy connectable(engine/connection) ordatabase string URI or sqlite3 DBAPI2 connectionother DBAPI2 objects are not tested, please consider using SQLAlchemy
#

from sqlalchemy import create_engine

uri = f'mysql+mysqlconnector://{env["DB_USER"]}:{env["DB_PWD"]}@{env["DB_HOST"]}/{env["DB_NAME"]}'
db = create_engine(uri, echo=True)


def query_to_df(query):
    with db.connect() as connection:
        result = pd.read_sql_query(query, connection)
        return pd.DataFrame(result)


studies = query_to_df('''SELECT * FROM studies;''')
studies.head(1)

tables = query_to_df("show tables;")

# ## Now we want to create an empty data frame with all the measures as columns

import json

with open ("./measures.json") as file:
    measures = json.loads(file.read())

df_measures = pd.DataFrame()
for measures_group in measures:
        for measure in measures_group['labels']:
                print("This is the id:", measure['id'], "This is the measure name:" ,measure['name_en'])
                break

# +
all_individuals = pd.DataFrame()
for measures_group in measures:
        for measure in measures_group['labels']:
                measure = pd.DataFrame([], columns={ measure['id']})
                all_individuals = pd.concat([all_individuals, measure],ignore_index=True, axis=0)

all_individuals.insert(0, 'Individual id', pd.Series)
all_individuals
# -

# ## Here we get all the measurements from the table

m = query_to_df("SELECT * FROM measurements")

individual_id = 0
for i, row in m.iterrows():
    if row['individual_id'] == 1:
        print(row)
    else:
        break
    

def add_individual(data, row):
    pass
    return pd.concat([data, measure],ignore_index=True, axis=0)


# +
def create_individual():
    pd.concat


# -

# Variant one general workflow
# Create study dataframe for each study id


# Variant two general workflow
# Create a big dataframe with all individuals
    # Create the dataframe with each of the measures columns as numbers
    # Populate the dataframe by iterating over each measure and adding the value to the dataframe
# Then create separate dataframe for each study
