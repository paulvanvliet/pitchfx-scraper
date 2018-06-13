import scrape
import datetime
import db_ops
from datetime import date

try:
    import configs
except ImportError:
    print('Check to make sure configs file is in same directory as main.py')
    exit()
else:
    if configs.db_path == "":
        print('Please set db_path in config file to absolute path to database')
        exit()
    elif configs.sql_create == "":
        print('Please set sql_create in config file to absolute path to '
              'pitches.sql')
        exit()


def get_date_from_user(which):
    """
        Get user input to build a datetime object. This will be used
        as the starting date of the scraping.
    """
    if which == 'start':
        print("Please enter start date in form: year-month-day")
    elif which == 'end':
        print("Please enter end date in form: year-month-day")
    uin = input()
    try:
        start_date = datetime.datetime.strptime(uin, '%Y-%m-%d').date()
    except ValueError:
        print("Incorrect format. Please try again.")
        return get_date_from_user(which)
    return start_date


def daterange(start_date, end_date):
    """
        This function allows for iteration over a date range
        defined by start and end arguments
    """
    for n in range(int((end_date-start_date).days)):
        yield start_date + datetime.timedelta(n)

if __name__ == '__main__':
    cursor, conn = db_ops.db_connect(configs.db_path)
    cleared = db_ops.clear_prompt(cursor)
    db_ops.table_check(cursor, configs.sql_create)
    if cleared == 'y':
        start = get_date_from_user('start')
    else:
        start = db_ops.get_last_date(cursor)
    end = get_date_from_user('end')
    for i in daterange(start, end):
        print(i)
        games = scrape.get_files_web(i.year, i.month, i.day)
        try:
            for game in games:
                data = scrape.parse_pitches(game, i.year, i.month, i.day)
                for pitch in data:
                    db_ops.db_insert(cursor, configs.columns, pitch)
        except:
            pass
    
    conn.commit()
    conn.close()
