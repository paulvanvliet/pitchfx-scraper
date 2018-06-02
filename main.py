# -*- coding: utf-8 -*-
"""
"""

from scrape import *
from datetime import timedelta, date
import datetime
import pandas as pd
import sqlite3
import configs


def get_date_from_user(which):
    '''
        Get user input to build a datetime object. This will be used
        as the starting date of the scraping.
    '''
    if which == 'start':
        print("Please enter start date in form: year-month-day")
    elif which == 'end':
        print("Please enter end date in form: year-month-day")

    uin = input()

    try:
        start = datetime.datetime.strptime(uin, '%Y-%m-%d').date()
    except ValueError:
        print("Incorrect format. Please try again.")
        return get_date_from_user()

    return start

def daterange(start, end):
    '''
        This function allows for iteration over a date range
        defined by start and end arguments
    '''
    for n in range(int ((end-start).days)):
        yield start + timedelta(n)


if __name__ == '__main__':
    start = get_date_from_user('start')
    end = get_date_from_user('end')
    big_data = []

    conn = sqlite3.connect(configs.db_path)
    c = conn.cursor()
    qry = open(configs.sql_create).read()
    c.execute(qry)
    for i in daterange(start, end):
        print(i)
        games = get_files_web(i.year, i.month, i.day)
        try:
            for game in games:
                holders = ','.join('?' * y)
                sql = 'INSERT INTO ' + configs.table_name + VALUES({0})'.format(holders)
                c.execute(sql, tuple(parse_pitches(game, i.year, i.month, i.day)))
        except:
            pass

    #df = pd.DataFrame(big_data, columns=headers())
    #df.to_csv('C:/Projects/Baseball/Pitchfx/Data/allpitches2018.csv')
