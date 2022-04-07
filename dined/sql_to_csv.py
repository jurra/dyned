'''
Convert results from sql queries to csv files
'''
import sys

import os 
from os import environ as env

import mysql.connector
from mysql.connector import Error

import pandas as pd

from dotenv import load_dotenv
load_dotenv()

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
    write(sys.argv[1], sys.argv[2])

