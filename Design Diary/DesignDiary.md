# Design Diary - Car Data Analysis - 03/13/2020

For this assignment, we were tasked with using pandas and jupyter notebook to do data analysis on a specific dataset. For my project, I wanted to look at how used car prices from Craigslist are affected by the population of the location that the car is listed in. To do this, I started by taking population data from [California Demographics by city](https://www.california-demographics.com/cities_by_population) and translating their population table into a database table. Next I needed to create the links for every California Craigslist region. I did this by pulling a list from [Craigslist](https://geo.craigslist.org/iso/us/ca), and writing the links to a file (clinks.txt). Next I created paginated links for each region's link by reading the clinks.txt file and pulling the total number of listings per link and the number of listings per page. I then wrote new links to paglinks.txt using the following code:

```num_pages = soup.find_all('span', attrs={"class" : "totalcount"})[0].string
count_by = soup.find_all('span', attrs={"class" : "rangeTo"})[0].string
                f.write(url + '\n')
                url_ext = '?s='
                counter = int(count_by)
                while int(num_pages) - counter > 0:
                    f.write(url + url_ext + '{}'.format(counter) + '\n')
                    counter += int(count_by)
```

This allowed me to read the file and pull data from each page of listings from every region, originally I pulled each url, each price, and the location of the listing. Because my data seemed to be inaccurate, as people didn't properly list their location, I created a new branch so that I could grab data from [California Demographics by county](https://www.california-demographics.com/counties_by_population), and use that to write a database table for populations of each regions. For this, I used google to put the counties in every region in a table nxt to the region name. Then I used a function to run through the demographic data and database and update the database by adding to the unused population column. Then instead of grabbing the location from the bottom of the post, I grabbed the region name from the url and used that to query the region population. This edit netted me almost 7,000 more listings, however for probably a bunch of reasons, the .corr() function showed that there was essentially no correlation between price and location population. This was probably the most challenging part of the assignment because I really had no idea where to go from there, so I just concluded my project. Despite being one of the more disappointing projects that I've worked on, the database writing and webscraping was really fun and I did enjoy that part a lot.