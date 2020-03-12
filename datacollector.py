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
    f = open('popdatabycounty.csv', 'w')
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
                    f.write(cell + ',')
                column_count += 1
        f.write('\n')
    f.close()

def write_to_db(csv_file):
    open_csv = open(csv_file)
    csv_reader = csv.reader(open_csv, delimiter=',')
    conn = sqlite3.connect('cities.db')
    curs = conn.cursor()
    curs.execute('''CREATE TABLE IF NOT EXISTS counties
                    (id INTEGER PRIMARY KEY, county STRING, county_pop INTEGER)''')
    count = 1
    for row in csv_reader:
        try:
            row[1]
        except:
            pass
        else:
            query = ('''INSERT INTO "counties"
                        VALUES (?,?,?)''')
            query_data = (count, row[0], int(row[1]))
            curs.execute(query, query_data)
            count += 1
    open_csv.close()
    conn.commit()
    conn.close()

def write_total_populations():
    conn = sqlite3.connect('cities.db')
    curs = conn.cursor()
    curs.execute('''SELECT counties FROM "craigslistcounties"''')
    counties = curs.fetchall()
    count = 1
    for countydata in counties:
        countydata = countydata[0].split(', ')
        total_pop = 0
        for county in countydata:
            curs.execute('''SELECT county_pop FROM "counties"
                            WHERE county=?''', (county,))
            curr_pop = curs.fetchone()
            total_pop += curr_pop[0]
        curs.execute('''UPDATE craigslistcounties SET population={} WHERE id={}'''.format(total_pop, count))
        count += 1
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
                            listing_location = listing_url.split('//')[1].split('.')[0]
                            curs.execute("""SELECT population FROM "craigslistcounties"
                                            WHERE clregion=?""",
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
    # write_population_data()
    # write_to_db('popdatabycounty.csv')
    # write_total_populations()
    # write_paginated_links()
    build_db()