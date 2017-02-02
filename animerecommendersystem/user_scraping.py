import os
from bs4 import BeautifulSoup
import json

import definitions

# Constants
ANIME_ID_FIELD = 'anime_id'
RATE_FIELD = 'rate'
CURR_STATE_FIELD = 'curr_state'

# Initialize the JSON as empty
users_json = {}


def add_anime(username, anime_id, rate, curr_state):
    """
    :param username: name of the user of which we're going to modify the list.
    :param anime_id: id of the anime to be added to user's list.
    :param rate: from 0 to 10, represents the grade given by the user to that anime. Zero means no rate.
    :param curr_state: completed, current, dropped and so on.
    :return: updates the sparse matrix of users, and returns nothing.
    """
    anime_record = {
            RATE_FIELD: rate,
            CURR_STATE_FIELD: curr_state,
    }

    if users_json.get(username) is None:
        users_json[username] = {}

    users_json[username][anime_id] = anime_record


def scrape_page(file_name):
    """
    :param file_name: name of file containing a user anime list
    :return: calls add_anime for this user and for each anime in this anime_list
    """
    htmlfile = os.path.join(definitions.USERS_DIR, file_name)
    fh = open(htmlfile, "r")
    username = file_name[:len(file_name) - 5]
    print username
    soup = BeautifulSoup(fh, 'html.parser')

    # we have only json users
    json_animes = soup.find_all('table', attrs={'data-items': True})
    # print json_animes

    # print json_animes[0]['data-items']
    x = json.loads(json_animes[0]['data-items'])
    # print x
    for j in x:
        id = j['anime_url'][7:len(j['anime_url'])].split('/')[0]
        rate = j['score']
        state = j['status']
        add_anime(username, id, rate, state)


if __name__ == '__main__':
    # where users' anime-lists are stored
    users_anime_lists = os.listdir(definitions.USERS_DIR)

    for f in users_anime_lists:
        scrape_page(f)

    #filename = os.path.join(definitions.FILE_DIR, definitions.JSON_USER_FILE)
    filename = definitions.JSON_USER_FILE
    outfile = open(filename, 'wb')
    json.dump(users_json, outfile)


''' Caso scraping strano: DA BUTTARE SE USIAMO SOLO JSON
try:
    list_anime_title_id = soup.find_all('a', href=lambda value: value.startswith('/anime/'))
except AttributeError:
    # empty list
    list_anime_title_id = list()

list_anime_rating = list()
title = list()
id = list()
for anime in list_anime_title_id:
    #   anime['href'] is like /anime/id/title, so I take only the substring after the 6th character (id/title)
    #   and then I split by /, taking just the first part, that is the id.
    #   For the title i pick the second part
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
'''