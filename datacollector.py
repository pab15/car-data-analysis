import re
import csv
import ssl
import urllib
import sqlite3
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
# import pandas as pd

def write_population_data():
    result = []
    url = 'https://www.california-demographics.com/counties_by_population'
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

def build_db():
    conn = sqlite3.connect('cities.db')
    curs = conn.cursor()
    curs.execute('''CREATE TABLE IF NOT EXISTS listings
                    (id INTEGER PRIMARY KEY, url STRING, price INTEGER, location_pop INTEGER)''')
    count = 1
    with open('paglinks.txt') as paglinks:
        for line in enumerate(paglinks):
            if line != '':
                url = line[1].strip('\n')
                result = []
                response = urllib.request.urlopen(url)
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                listings = soup.find_all('li', attrs={"class" : "result-row"})
                for listing in listings:
                    listing_url = str(listing.find('a'))
                    listing_url = listing_url.split('"')
                    try:
                        listing_url = listing_url[5]
                    except:
                        for value in listing_url:
                            if 'https://' in value:
                                listing_url = value
                    else:
                        curs.execute("""SELECT url FROM "listings"
                                                WHERE url=?""",
                                                (listing_url,))
                        result_url = curs.fetchone()
                        if result_url:
                            pass
                        else:
                            try:
                                listing_location = str(listing.find('span', attrs = {"class" : "result-hood"}).string)
                            except:
                                pass
                            else:
                                if listing_location != '':
                                    listing_location = str(listing.find('span', attrs = {"class" : "result-hood"}).string)
                                    listing_location = listing_location.strip(')')
                                    listing_location = listing_location[2:]
                                    if '/' in listing_location:
                                        listing_location = listing_location.split('/')
                                        listing_location = listing_location[0]
                                        listing_location = listing_location.split()
                                        for x in range(len(listing_location)):
                                            first_letter = listing_location[x][0].upper()
                                            rest = listing_location[x][1:].lower()
                                            listing_location[x] = str(first_letter) + str(rest)
                                        sep = ' '
                                        listing_location = sep.join(listing_location)
                                    if '(' in listing_location or ')' in listing_location:
                                        listing_location = listing_location.split('(', 1)[0]
                                    listing_location = listing_location.split(' ')
                                    for x in range(len(listing_location)):
                                        if x != '' or ' ':
                                            try:
                                                first_letter = listing_location[x][0].upper()
                                                rest = listing_location[x][1:].lower()
                                                listing_location[x] = str(first_letter) + str(rest)
                                            except:
                                                pass
                                            else:
                                                first_letter = listing_location[x][0].upper()
                                                rest = listing_location[x][1:].lower()
                                                listing_location[x] = str(first_letter) + str(rest)
                                    sep = ' '
                                    listing_location = sep.join(listing_location)
                                    if ',' in listing_location:
                                        listing_location = listing_location.split(',', 1)[0]
                                    if ' ca' in listing_location:
                                        listing_location = listing_location.replace(' ca', '')
                                    if ' Ca' in listing_location:
                                        listing_location = listing_location.replace(' Ca', '')
                                    if ' CA' in listing_location:
                                        listing_location = listing_location.replace(' CA', '')
                                    if '.ca' in listing_location:
                                        listing_location = listing_location.replace('.ca', '')
                                    if 'SW ' in listing_location:
                                        listing_location = listing_location.replace('SW ', '')
                                    if ' SW' in listing_location:
                                        listing_location = listing_location.replace(' SW', '')
                                    if 'SW' in listing_location:
                                        listing_location = listing_location.replace('SW', '')
                                    if 'Sw ' in listing_location:
                                        listing_location = listing_location.replace('Sw ', '')
                                    if ' Sw' in listing_location:
                                        listing_location = listing_location.replace(' Sw', '')
                                    if 'Sw' in listing_location:
                                        listing_location = listing_location.replace('Sw', '')
                                    if 'sw ' in listing_location:
                                        listing_location = listing_location.replace('sw ', '')
                                    if ' sw' in listing_location:
                                        listing_location = listing_location.replace(' sw', '')
                                    if 'sw' in listing_location:
                                        listing_location = listing_location.replace('sw', '')
                                    if 'NW ' in listing_location:
                                        listing_location = listing_location.replace('NW ', '')
                                    if ' NW' in listing_location:
                                        listing_location = listing_location.replace(' NW', '')
                                    if 'NW' in listing_location:
                                        listing_location = listing_location.replace('NW', '')
                                    if 'Nw ' in listing_location:
                                        listing_location = listing_location.replace('Nw ', '')
                                    if ' Nw' in listing_location:
                                        listing_location = listing_location.replace(' Nw', '')
                                    if 'Nw' in listing_location:
                                        listing_location = listing_location.replace('Nw', '')
                                    if 'nw ' in listing_location:
                                        listing_location = listing_location.replace('nw ', '')
                                    if ' nw' in listing_location:
                                        listing_location = listing_location.replace(' nw', '')
                                    if 'nw' in listing_location:
                                        listing_location = listing_location.replace('nw', '')
                                    if ' and ' in listing_location:
                                        listing_location = listing_location.split(' and ')
                                        listing_location = listing_location[0]
                                    curs.execute("""SELECT population FROM "city"
                                                    WHERE city=?""",
                                                    (listing_location,))
                                    result = curs.fetchone()
                                    if result: 
                                        location_pop = int(result[0])
                                        listing_price = str(listing.find('span', attrs = {"class" : "result-price"}).string)
                                        listing_price = listing_price.replace('$', '')
                                        if listing_price != '' and listing_price != '0' and listing_price != '1':
                                            try:
                                                listing_price = int(listing_price)
                                            except:
                                                pass
                                            else: 
                                                listing_price = int(listing_price)
                                        query = ('''INSERT INTO "listings"
                                                    VALUES (?,?,?,?)''')
                                        query_data = (count, listing_url, listing_price, location_pop)
                                        curs.execute(query, query_data)
                                        conn.commit()
                                        count += 1
    conn.close()

if __name__ == '__main__':
    write_population_data()
    # write_to_db('popdatabycity.csv')
    # build_db()