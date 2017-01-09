import os
from bs4 import BeautifulSoup
import re

''' Where users' anime lists are '''
PATH = "D:\\users"

users_anime_lists = os.listdir(PATH)
#for file in users_anime_list:
fh = open(PATH+"\\FellOn.html", "r")
soup = BeautifulSoup(fh, 'html.parser')

list_json_animes = soup.find_all('table', attrs={'data-items': True})
print list_json_animes
try:
    list_anime_title_id = soup.find_all('a', href=lambda value: value.startswith('/anime/'))
except AttributeError:
    # empty list
    list_anime_title_id = list()

''' Caso strano '''
list_anime_rating = list()
title = list()
id = list()
for anime in list_anime_title_id:
    ''' anime['href'] is like /anime/id/title, so I take only the substring after the 6th character (id/title)
        and then I split by /, taking just the first part, that is the id.
         For the title i pick the second part'''
    id.append(anime['href'][7:len(anime['href'])].split('/')[0])
    title.append(anime['href'][7:len(anime['href'])].split('/')[1])
    # parent tag, which is a <td> tag
    tag = anime.parent
    rating_tag = tag.findNext('td')
    cleanString = re.sub('["\n", " "]', '', rating_tag.string)
    list_anime_rating.append(cleanString)

print list_anime_rating
print title
print id


''' Json pages '''
json_animes = list()
for anime in list_json_animes:
    json_animes.append(anime['data-items'])
print json_animes

