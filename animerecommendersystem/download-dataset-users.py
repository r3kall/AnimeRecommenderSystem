"""
Download users' anime lists from myanimelist.net, from 11 countries spread all over the world.
"""

import urllib2
import re
import os
from bs4 import BeautifulSoup
import definitions


def check_json_presence(html_page):
    """
    This function is used to select only users with an anime list easy to process.
    :param html_page: self-explaining
    :return: True if the html code of user's anime list has a json in it, or False otherwise.
    """
    soup = BeautifulSoup(html_page, 'html.parser')
    json_table = soup.find_all('table', attrs={'data-items': True})
    return len(json_table) > 0


if not os.path.exists(definitions.FILE_DIR):
    os.makedirs(definitions.FILE_DIR)
if not os.path.exists(definitions.USERS_DIR):
    os.makedirs(definitions.USERS_DIR)

# contains recently online users and search bar for users
url = "https://myanimelist.net/users.php"

list_of_countries = ["Italy", "USA", "Germany", "Japan", "Brasil", "Russia",
                     "Greece", "Saudi Arabia", "Egypt", "England", "Mexico"]

for country in list_of_countries:
    print country
    # search users by country, age and gender don't care
    country_url = url + "?q=&loc=" + country + "&agelow=0&agehigh=0&g="
    print country_url

    # this is to avoid blocking because of http errors, try to connect until 10 attempts
    attempts_1 = 0
    while attempts_1 < 10:
        try:
            response_1 = urllib2.urlopen(country_url)
            break
        except urllib2.HTTPError, e:
            attempts_1 += 1

    # read
    html_1 = response_1.read()

    # search for urls in the page, corresponding to the form /profile/[name_of_user], these are user profiles
    users_1 = re.findall('''href=["'](/profile/[0-9a-zA-Z|_\-]+)["']''', html_1, re.UNICODE)
    users = list()

    # since each url is present twice in the page, i pick each user only once
    for t in range(len(users_1) / 2):
        users.append(users_1[t * 2])
    print users

    # users in each page
    users_per_page = 24

    # users i saw until now
    current_users = 24

    # num pages to crawl
    num_pages = 5

    # search in num_pages pages
    while current_users <= users_per_page*num_pages:
        # url is slightly different from previous one
        country_url = url + "?q=&loc=" + country + "&agelow=0&agehigh=0&g=&show="+str(current_users)
        # print country_url

        # this is to avoid blocking because of http errors, try to connect until 10 attempts
        attempts_1 = 0
        while attempts_1 < 10:
            try:
                response_1 = urllib2.urlopen(country_url)
                break
            except urllib2.HTTPError, e:
                attempts_1 += 1

        # read
        html_1 = response_1.read()

        # search for urls in the page, corresponding to the form /profile/[name_of_user], these are user profiles
        users_2 = re.findall('''href=["'](/profile/[0-9a-zA-Z|_\-]+)["']''', html_1, re.UNICODE)
        # print users_2

        # since each url is present twice in the page, i pick each user only once
        for t in range(len(users_2)/2):
            users.append(users_2[t*2])
        current_users += users_per_page

    # print users

    # write to a local file
    for user in users:
        print user
        # file to be written to
        filename = os.path.join(definitions.USERS_DIR,
                                user[9: len(user)] + ".html")

        # this is to avoid blocking because of http errors,
        # try to connect until 10 attempts
        attempts_2 = 0
        while attempts_2 < 10:
            try:
                user_profile = urllib2.urlopen("https://myanimelist.net/animelist/" + user[9: len(user)])
                user_profile_html = user_profile.read()
                # download only users with a json format profile
                flag = check_json_presence(user_profile_html)
                print flag
                if flag:
                    # open the file for writing
                    fh = open(filename, "w")

                    # write to file
                    fh.write(user_profile_html)
                    fh.close()
                break
            except urllib2.HTTPError, e:
                print attempts_2
                attempts_2 += 1
