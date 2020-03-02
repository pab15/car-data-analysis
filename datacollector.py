import re
import csv
import ssl
import urllib
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import pandas as pd

def write_population_data():
    result = []
    url = 'https://www.california-demographics.com/zip_codes_by_population'
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('table')[0]
    row_count = 0
    f = open('popdatabyzip.csv', 'w')
    tr_data = data.find_all('tr')
    for row in tr_data:
        columns = row.find_all('td')
        for column in columns:
            cell = column.get_text().strip()
            cell = cell.replace(',', '')
            f.write(cell + ',')
        f.write('\n')
    f.close()

def pullZipCodeListings():
        pass

if __name__ == '__main__':
    write_population_data()