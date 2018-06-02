# -*- coding: utf-8 -*-
"""
"""
import re
from bs4 import BeautifulSoup, SoupStrainer
from urllib2 import urlopen

"""
First, for each day get all of the game IDs
"""

def headers():
    headers = ['year', 
               'month', 
               'day', 
               'away_team', 
               'home_team', 
               'inning',
               'half',
               'away_team_runs',
               'home_team_runs',
               'batter',
               'pitcher',
               'stand',
               'p_throws',
               'b',
               's',
               'o',
               'ab_des',
               'event', 
               'r1',
               'r2',
               'r3',
               'rbi',
               'r2r3',
               'balls',
               'strikes',
               'pitch_des',
               'id',
               'type',
               'code',
               'tfs',
               'x',
               'y',
               'start_speed',
               'end_speed',
               'sz_top',
               'sz_bot',
               'pfx_x',
               'pfx_z',
               'px',
               'pz',
               'x0',
               'y0',
               'z0',
               'vx0',
               'vy0',
               'vz0',
               'ax',
               'ay',
               'az',
               'break_y',
               'break_angle',
               'break_length',
               'pitch_type',
               'type_confidence',
               'zone',
               'nasty',
               'spin_dir',
               'spin_rate',
               ]
    return headers

def make_url(year, month, day):
    baseurl = 'http://gd2.mlb.com/components/game/mlb/'    
    url = baseurl+'year_'+str(year)+'/month_'+'%02d'%month+'/day_'+'%02d' %day
    return url


def get_page(url):
    '''
        Safely attempt to get the page at the given URL
    '''
    try:
        f = urlopen(url)
    except:
        return False
    return f

def get_links(url):
    '''
        Get all the links off of the page:
        gd2.mlb.com/components/game/mlb/year/month/day/
        
        And finds the links for the games that have the following 
        format:
   
        gid_year_mm_dd_team1mlb_team2mlb   
    '''
    f = get_page(url)
    if f==False: return False
    
    # Compile the regex to match links outside of the loop for performance
    links = []
    regex = re.compile("\".*?gid_(.*?)\"", re.IGNORECASE)
    
    # Find all links on page and if they are links to games then add to list
    for link in BeautifulSoup(f, "lxml",
                              parse_only=SoupStrainer('a', href=True)):
        match = regex.findall(str(link))
        
        if match:
            links.extend(match)
   
    return links

def get_files_web(year, month, day):
    url = make_url(year, month, day)
      
    links = get_links(url)
    if links == False:
        print("Could not get links on page: " + url)
        return False
    
    games = []
    for link in links:
        full_url = url + "/gid_" + link 
        games_parsed = []
        
        # Loop through the files we need to get
        page = get_page(full_url + "inning/inning_all.xml")
        if page == False: return False

        games_parsed = BeautifulSoup(page, "lxml")
        
        games.append(games_parsed)

    return games

def parse_runners(tags):
    '''
        Parse all the <runner> tags from the <atbat> tags to get 
        the information about the current runners on base for the atbat.
        Return a list of the information so it may be appended to the running
        list
    '''
    r1 = r2 = r3 = rbi = 0
    
    for r in tags:
        if r['start'] == '1B':
            r1 = 1
        elif r['start'] == '2B':
            r2 = 1
        elif r['start'] == '3B':
            r3 = 1
        
        try: 
            if r['rbi'] == 'T': rbi = rbi + 1
        except: pass

    return [r1, r2, r3, rbi, r2+r3]


def get_abinfo(soupobject):
    ab_fields = ['away_team_runs',
                 'home_team_runs',
                 'batter',
                 'pitcher',
                 'stand',
                 'p_throws',
                 'b',
                 's',
                 'o',
                 'des',
                 'event']
    abinfo = []
    for field in ab_fields:
        try:
            abinfo.append(str(soupobject[field]))
        except:
            abinfo.append('')
    return abinfo

def get_pitchinfo(soupobject):
    pitch_fields = ['des',
                    'id',
                    'type',
                    'code',
                    'tfs',
                    'x',
                    'y',
                    'start_speed',
                    'end_speed',
                    'sz_top',
                    'sz_bot',
                    'pfx_x',
                    'pfx_z',
                    'px',
                    'pz',
                    'x0',
                    'y0',
                    'z0',
                    'vx0',
                    'vy0',
                    'vz0',
                    'ax',
                    'ay',
                    'az',
                    'break_y',
                    'break_angle',
                    'break_length',
                    'pitch_type',
                    'type_confidence',
                    'zone',
                    'nasty',
                    'spin_dir',
                    'spin_rate'
                    ]
    pitchinfo = []
    for field in pitch_fields:
        try:
            pitchinfo.append(str(soupobject[field]))
        except:
            pitchinfo.append('')
    return pitchinfo
    
def parse_pitches(soup, year, month, day):
    '''
        Parse the pitchfx data from the innings/innings_all.xml. This function 
        finds the atbat information, and the corresponding pitch data for the at
        bat. It also gets other information such as the runners that are on base.
        
        Returns all of the pitches from a particular game
    '''
    gamedata = []
    innings = soup.find_all('inning')
    for inning in innings:
        info = [year, month, day, inning['away_team'], inning['home_team'],
                inning['num'],'']
        
        for half in ['top', 'bottom']:
            info[6] = half
            if half == 'top':
                try:
                    atbats = inning.top.find_all('atbat')
                except:
                    pass
            else:
                try:
                    atbats = inning.bottom.find_all('atbat')
                except:
                    pass
            for ab in atbats:
                abinfo = (info + get_abinfo(ab) +
                          parse_runners(ab.find_all('runner')))            
                balls = strikes = 0
            
                pitches = ab.find_all('pitch')
                for p in pitches:
                    pdata = (abinfo + [balls, strikes] + get_pitchinfo(p))
                    if p['type'] == 'B':
                        balls = balls + 1
                    elif p['type'] == 'S':
                        if strikes < 2: strikes = strikes + 1
                    gamedata.append(pdata)
    return gamedata
    
