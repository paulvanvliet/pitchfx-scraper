# -*- coding: utf-8 -*-
import sqlite3
import datetime
#from pathlib import Path


def check_configs(path):
    """

    :param path: path to configs file
    :return: updated file
    
    try:
        Path(path).resolve()
    except FileNotFoundError:
        print('Config file not found. Check path.')
        return False
    else:
        return True
    """
    return True

def db_insert(cursor, columns, data):
    """
    INPUTS:
        cursor: Connection to the sqlite database
        columns: Tuple of column names
        data: list of values to the inserted into database
    """
    var_string = ', '.join('?' * len(data))
    query_string = 'INSERT INTO pitches %s VALUES (%s);'%(columns, var_string)
    try:    
        cursor.execute(query_string, data)
    except sqlite3.Error as e:
        print('Data could not be inserted: %s' %e)
        return


def db_clear(cursor):
    """
    INPUTS:
        cursor: Connection to sqlite database
    """
    try:
        cursor.execute('DROP TABLE IF EXISTS pitches')
    except sqlite3.Error as e:
        print('Database could not be cleared %s' %e)


def get_last_date(cursor):
    cursor.execute('SELECT MAX(date) FROM pitches;')
    date1 = cursor.fetchone()
    date2 = datetime.datetime.strptime(str(date1[0]), '%Y-%m-%d').date()
    date2 = date2 + datetime.timedelta(days=1)
    return date2


def db_connect(path):
    try:
        conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
    except sqlite3.Error as e:
        print('No connection to database: %s' %e)
    else:
        return c, conn


def table_check(cursor, table_sql):
    """
    table_sql is a .sql file containing the sql code to create a table
    if it doesn't already exist
    """
    qry = open(table_sql).read()
    cursor.execute(qry)
    

def clear_prompt(cursor):
    answer = input('Would you like to clear the db? [y/n]')    
    if answer == 'y':
        db_clear(cursor)
    elif answer == 'n':
        pass
    else:
        clear_prompt(cursor)
    return answer


def get_all_dates(cursor):
    qry = "SELECT DISTINCT date FROM pitches"
    cursor.execute(qry)
    dates = set(cursor.fetchall())
    return dates
