import re
import csv
import ssl
import urllib
import sqlite3
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import pandas as pd

def write_population_data():
    result = []
    url = 'https://www.california-demographics.com/cities_by_population'
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('table')[0]
    row_count = 0
    f = open('popdatabycity.csv', 'w')
    tr_data = data.find_all('tr')
    for row in tr_data:
        columns = row.find_all('td')
        column_count = 0
        for column in columns:
            cell = column.get_text().strip()
            if cell[:6] != 'The ta' and cell[:6] != 'United':
                if column_count == 2:
                    cell = cell.replace(',', '')
                    f.write(cell + ',')
                if column_count == 1:
                    cell = cell.replace(', ', '-')
                    cell = cell.replace(' and ', '-')
                    cell = cell.replace('and ', '')
                    if '(' in cell:
                        cell = cell.split('(')
                        cell = cell[1].strip(')')
                        f.write(cell + ',')
                    else:
                        f.write(cell + ',')
                column_count += 1
        f.write('\n')
    f.close()

def write_to_db(csv_file):
    open_csv = open(csv_file)
    csv_reader = csv.reader(open_csv, delimiter=',')
    conn = sqlite3.connect('cities.db')
    curs = conn.cursor()
    curs.execute('''CREATE TABLE IF NOT EXISTS city
                    (id INTEGER PRIMARY KEY, city STRING, population INTEGER)''')
    count = 1
    for row in csv_reader:
        if row != []:
            if '-' in row[0]:
                cities = row[0].split('-')
                for city in cities:
                    query = ('''INSERT INTO "city"
                                VALUES (?,?,?)''')
                    query_data = (count, str(city), int(row[1]))
                    curs.execute(query, query_data)
                    conn.commit()
                    count += 1
            else:
                query = ('''INSERT INTO "city"
                            VALUES (?,?,?)''')
                query_data = (count, str(row[0]), int(row[1]))
                curs.execute(query, query_data)
                conn.commit()
                count += 1
    open_csv.close()
    conn.commit()
    conn.close()

def grab_links():
    file = open('clinks.txt', 'w')
    result = []
    url = 'https://geo.craigslist.org/iso/us/ca'
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    locations = soup.find_all('ul')[1]
    link_ext = '/search/cto/'
    for l in locations:
        l.find('a')
        for link in l:
            link = str(link).split('"')
            if len(link) > 1:
                link = link[1] + '{}'.format(link_ext)
                file.write(link + '\n')
    file.close()

def write_paginated_links():
    f = open('paglinks.txt', 'w')
    with open('clinks.txt') as clinks:
        for line in enumerate(clinks):
            if line != '':
                url = line[1].strip('\n')
                response = urllib.request.urlopen(url)
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                num_pages = soup.find_all('span', attrs={"class" : "totalcount"})[0].string
                count_by = soup.find_all('span', attrs={"class" : "rangeTo"})[0].string
                f.write(url + '\n')
                url_ext = '?s='
                counter = int(count_by)
                while int(num_pages) - counter > 0:
                    f.write(url + url_ext + '{}'.format(counter) + '\n')
                    counter += int(count_by)
    f.close()

if __name__ == '__main__':
    # write_population_data()
    # write_to_db('popdatabycity.csv')
    write_paginated_links()