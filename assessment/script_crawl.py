import requests
from bs4 import BeautifulSoup as bs, SoupStrainer
import pandas as pd
from sortedcollections import OrderedSet
import re

import pyodbc
import sqlalchemy
from sqlalchemy import create_engine

def title_ratingExtract(url):
    '''
    This function returns the casts, title, year, genre and rating columns from the imdb website

    '''
    page = requests.get(url).text
    soup = bs(page, 'lxml')
    target_table = soup.find('table', attrs={'class':'chart full-width'})
    table_rows = target_table.find_all("tr")
    res = []
    for tr in table_rows:
        td = tr.find_all('td')
        row = [tr.text.strip() for tr in td if tr.text.strip()]
        if row:
            res.append(row)
    df = pd.DataFrame(res,columns=['title','rating','drop'])
    df = df.drop('drop',axis=1)
    df['title'] = [df['title'][x].split('.\n')[-1].replace(' ', '').replace('\n',' ') for x in range(len(df))]
    df[['title','year']] = df['title'].str.split('\(|\)',expand=True).iloc[:,[0,1]]
    df['title'] = df['title'].str.strip()
    
    #'''
    souptd = bs(page, parseOnlyThese=SoupStrainer("td"))
    x = souptd.findAll("a")
    res = []
    for tr in x:
        link = 'https://www.imdb.com' + tr.get('href')
        res.append(link)
    res = list(OrderedSet(res))
    df['url'] = res
    df['code'] = [i[27:-1] for i in df['url']]
    #'''
    return df

def casts(df,position):
    '''
    This functions assigns the actors starred in each movie
    '''
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0"}
    urlcast = df['url'][position] + 'fullcredits'
    actors = (
        bs(requests.get(urlcast, headers=headers).text, "lxml")
        .find('table', class_='cast_list')
        .select("a img")
    )
    genre = (
            bs(requests.get(df['url'][position], headers=headers).text, "lxml")
            .find('span', class_='ipc-chip__text')
            )
    genre_extract = re.search(r'(?<=text">)(.*)(\<)',str(genre)).group(0).replace('<','')
    actors_res = [actors[i]['title'] for i in range(len(actors))]
    df_actors = pd.DataFrame(actors_res, columns=['casts'])
    df_actors['title'] = df['title'][position]
    df_actors['year'] = df['year']
    df_actors['genre'] = genre_extract
    df_actors['rating'] = df['rating'][position]
    return df_actors

def revenue(code):
    '''
    This functions extracts the revenue from another website and assigns it to the respective movie
    '''
    page = requests.get('https://www.boxofficemojo.com/title/' + code +'/').text
    soup = bs(page, 'lxml')
    target_table = soup.find('div', attrs={'class':'a-section a-spacing-none mojo-performance-summary-table'})
    res = target_table.find_all('span',attrs={'class': 'money'})
    
    try: 
        total = int(res[-1].text.replace('$','').replace(',',''))
    except IndexError:
        total = 0
    
    return total
    