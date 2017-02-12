"""
user_item_matrix.py

This script build up the user-item matrix (NxM). In order to avoid (huge)
sparsity, the matrix is represented as a collection of lists.
"""

import os
import time
import json
from bs4 import BeautifulSoup

from animerecommendersystem.utils import definitions

# Constants
ANIME_ID_FIELD = 'anime_id'
RATE_FIELD = 'rate'
CURR_STATE_FIELD = 'curr_state'
MEAN_RATE = 'mean_rate'
LIST_FIELD = 'list'

# Initialize the JSON as empty
users_json = {}


def add_anime(username, anime_id, rate, curr_state):
    """
    :param username: name of the user of which we're going to modify the list.
    :param anime_id: id of the anime to be added to user's list.
    :param rate: from 0 to 10, represents the grade given by the user to
                 that anime. Zero means no rate.
    :param curr_state: completed, current, dropped and so on.
    :return: updates the sparse matrix of users, and returns nothing.
    """
    anime_record = {
            RATE_FIELD: rate,
            CURR_STATE_FIELD: curr_state,
    }

    if users_json.get(username) is None:
        users_json[username] = {}
    if users_json[username].get(LIST_FIELD) is None:
        users_json[username][LIST_FIELD] = {}

    users_json[username][LIST_FIELD][anime_id] = anime_record


def add_mean_rate(username, mean_rate):
    """This function add to 'users_json' dictionary the mean rate of an user"""
    users_json[username][MEAN_RATE] = mean_rate


def scrape_page(file_name):
    """
    Calls add_anime for this user and for each anime in this anime_list.

    :param file_name: name of file containing a user anime list
    """
    # directory of users html pages
    htmlfile = os.path.join(definitions.USERS_DIR, file_name)

    with open(htmlfile, 'r') as fh:
        username = file_name[:len(file_name) - 5]  # get username by filename
        soup = BeautifulSoup(fh, 'html.parser')

        # we have only json users
        json_animes = soup.find_all('table', attrs={'data-items': True})
        x = json.loads(json_animes[0]['data-items'])

        counter = 0
        rate_sum = 0
        for j in x:
            id = int(j['anime_url'][7:len(j['anime_url'])].split('/')[0])
            rate = int(j['score'])
            state = j['status']
            add_anime(username, id, rate, state)
            rate_sum += rate
            counter += 1

        # update mean rates
        if rate_sum != 0:
            users_json[username][MEAN_RATE] = float(rate_sum) / float(counter)
        else:
            if username in users_json.keys():
                users_json[username][MEAN_RATE] = 0.
            else:
                users_json[username] = {}
                users_json[username][LIST_FIELD] = {}
                users_json[username][MEAN_RATE] = 0.


def create_user_item_json():
    """
    This function create and save a JSON representation of
    the user-item matrix.
    """
    html_user_list = os.listdir(definitions.USERS_DIR)

    print "Generating user-item JSON file..."
    t0 = time.time()
    # for each html file in the users folder
    for hp in html_user_list:
        scrape_page(hp)

    with open(definitions.JSON_USER_FILE, 'w') as fp:
        j = json.dump(users_json, fp)

    t1 = time.time() - t0
    print "JSON file completed in:  %s" % str(t1)


if __name__ == '__main__':
    print __doc__
    create_user_item_json()
