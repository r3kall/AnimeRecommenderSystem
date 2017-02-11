"""
download-dataset-users.py
Download users' anime lists from myanimelist.net, from different countries
spread all over the world.
"""
import re
import os
import json
import time
import urllib2
from bs4 import BeautifulSoup
import animerecommendersystem.definitions

MIN_NUMBER_ANIME = 15  # Sampling and Selection of relevant users
MIN_NUMBER_USERS = 10000


if not os.path.exists(animerecommendersystem.definitions.FILE_DIR):
    os.makedirs(animerecommendersystem.definitions.FILE_DIR)
if not os.path.exists(animerecommendersystem.definitions.USERS_DIR):
    os.makedirs(animerecommendersystem.definitions.USERS_DIR)

# contains recently online users and search bar for users
url = "https://myanimelist.net/users.php"

list_of_countries = ["Italy", "USA", "Germany", "Japan", "Brasil", "Russia",
                     "Greece", "Saudi Arabia", "Egypt", "England", "Mexico", "Spain", "France",
                     "Argentina", "Ireland", "Australia", "South Africa", "Canada", "China", "Thailand",
                     "Albania", "Bangladesh", "India", "Denmark", "Romania", "Lebanon", "Ecuador",
                     "Austria", "Sweden", "Finland", "Switzerland", "Belgium", "Turkey", "Portugal",
                     "Bulgaria", "Colombia", "Croatia", "Israel", "Norway", "Scotland", "Malaysia", "Venezuela"]


def is_good_user(html_page):
    """
    This function is used to select only users with an anime list easy to process.
    :param html_page: self-explaining
    :return: True if the html code of user's anime list has a json in it, or False otherwise.
    """
    soup = BeautifulSoup(html_page, 'html.parser')
    json_table = soup.find_all('table', attrs={'data-items': True})
    if len(json_table) > 0:
        anime_json = json_table[0]['data-items']
        return has_enough_anime(anime_json)
    return False


def has_enough_anime(anime_list_json):
    """
    This function is used to select only users with at least X anime, so that they can be useful for recommendations.
    :param anime_list_json: self-explaining
    :return: True if the html code of user's anime list has enough animes, or False otherwise.
    """
    anime_dict = json.loads(anime_list_json)
    return len(anime_dict) > MIN_NUMBER_ANIME


def get_usernames(users_per_country, excluded):
    """Get usernames in order to download them later"""
    assert users_per_country > 1

    new_list = []

    def search_users(html_page):
        # search for urls in the page, corresponding to the
        # form /profile/[name_of_user], these are user profiles
        search = re.findall('''href=["'](/profile/[0-9a-zA-Z|_\-]+)["']''',
                            html_page, re.UNICODE)

        country_list = []
        # since each url is present twice in the page, i pick it only once
        for t in range(len(search) / 2):
            if t not in excluded:
                country_list.append(search[t * 2][9:])
        return country_list

    def attempts(url, tentatives=10):
        # this is to avoid blocking because of http errors,
        # try to connect until 10 attempts
        counter = 0
        while counter < tentatives:
            try:
                response = urllib2.urlopen(url)
                return response
            except urllib2.HTTPError:
                counter += 1
                time.sleep(2)
        return None

    for country in list_of_countries:
        print "Starting download from %s" % str(country)
        # search users by country, age and gender don't care
        country_url = url + "?q=&loc=" + country + "&agelow=0&agehigh=0&g="

        html_page = attempts(country_url).read()
        if html_page is None:
            continue

        country_list = search_users(html_page)  # populate users list
        user_count = len(country_list)

        users_per_page = 24  # users in each page
        current_users = 24  # users i saw until now
        num_pages = 21  # num pages to crawl

        # if limit is reached, then exit the loop
        if user_count >= users_per_country:
            continue

        # search in num_pages pages
        while current_users <= (users_per_page * num_pages):
            # if limit is reached, then exit the loop
            if user_count >= users_per_country:
                break

            # url is slightly different from previous one
            country_url = url + "?q=&loc=" + country + \
                          "&agelow=0&agehigh=0&g=&show=" + str(current_users)
            current_users += users_per_page

            html_page = attempts(country_url).read()
            if html_page is None:
                continue

            # search for urls in the page, corresponding to the
            # form /profile/[name_of_user], these are user profiles
            country_list += search_users(html_page)
            user_count = len(country_list)
        new_list += country_list
    return new_list


def download_user_lists(user_list):
    """Download lists of given users"""
    print "\nDownloading user lists..."
    download_count = 0
    for user in user_list:
        filename = os.path.join(animerecommendersystem.definitions.USERS_DIR, user + ".html")
        attempts = 0
        while attempts < 5:
            try:
                user_profile = urllib2.urlopen(
                    "https://myanimelist.net/animelist/" + user)
                user_profile_html = user_profile.read()
                # download only users with a json format profile
                if is_good_user(user_profile_html):
                    with open(filename, 'w') as fh:
                        fh.write(user_profile_html)  # write to file
                    download_count += 1
                break
            except urllib2.HTTPError:
                attempts += 1
                time.sleep(2)
    return download_count


def download_dataset_users():
    """Wrapper for download the user dataset"""
    total_count = 0
    excluded = os.listdir(animerecommendersystem.definitions.USERS_DIR)
    for u in range(len(excluded)):
        excluded[u] = excluded[u][:-5]
    print "Already downloaded users:  %d" % len(excluded)

    users = []
    while total_count < MIN_NUMBER_USERS:
        users = get_usernames(400, excluded + users)
        total_count += download_user_lists(users)
        print "Downloaded %d lists" % total_count
    return total_count


if __name__ == '__main__':
    print __doc__
    download_dataset_users()
