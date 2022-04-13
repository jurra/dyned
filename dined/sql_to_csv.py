'''
Exports data from sql dined database into a dataset of csv files.

In order to work with this script you need access to an instance of dined
database.

- We use mysql.connector package to connect to the database
- sql alchemy is required to use pandas with sql.
- The `measures.json` file contains a description of the measures which we use 
to create more descriptive csv files later 
'''
import sys

import os 
from os import environ as env

import mysql.connector
from mysql.connector import Error

import pandas as pd

from dotenv import load_dotenv
load_dotenv()

import json
from sqlalchemy import create_engine


uri = f'mysql+mysqlconnector://{env["DB_USER"]}:{env["DB_PWD"]}@{env["DB_HOST"]}/{env["DB_NAME"]}'
db = create_engine(uri, echo=True)

def read_measures_spec(path):
    with open (path) as file:
        return json.loads(file.read())

def get_data(query="""SELECT * FROM studies;"""):
    '''Do sql query'''
    try:
        connection = mysql.connector.connect(host=env['DB_HOST'],
                                            database=env['DB_NAME'],
                                            user=env['DB_USER'],
                                            password=env['DB_PWD'])
        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Connected to MsQL Server version ", db_info)
            cursor = connection.cursor()
            cursor.execute(query)
            records = cursor.fetchall()
            return records

    except Error as error:
        print("Error while connecting to MySQL", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def sql_to_df(query):
    with db.connect() as connection:
        result = pd.read_sql_query(query, connection)
        return pd.DataFrame(result)

def write(query, path, columns=None):
    '''Write query results to csv '''
    records = get_data(query)
    
    # Create dir if doesnt exist
    if not os.path.exists(path):
        dir ='/'.join(list(path.split('/')[:-1]))
        os.makedirs(dir)
        print("Created dir: ", path)

    df = pd.DataFrame(records, columns=columns)
    df.to_csv(path, index=False)
    print("Data written to csv file")
    print(df.head())


if __name__ == "__main__":
    measures = read_measures_spec('../experiments/measures.json')
    
    # Here we create an empty dataframe where each individual has a row with all measurements
    all_individuals = pd.DataFrame()
    for measures_group in measures:
        for measure in measures_group['labels']:
                measure = pd.DataFrame([], columns={ measure['id']})
                all_individuals = pd.concat([all_individuals, measure],ignore_index=True, axis=0)
        # all_individuals.insert(0, 'Individual id', pd.Series)
    
    m = sql_to_df("SELECT * FROM measurements")

    individual_id = 0
    for i, row in m.iterrows():
        if row['individual_id'] == 1:
            print(row)
        else:
            break

    # This function is deprecated as it is
    # write(sys.argv[1], sys.argv[2])


# Test conversion creation of dataframe for each individual