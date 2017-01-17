import urllib2
import re
from bs4 import BeautifulSoup


# contains recently online users and search bar for users
url = "https://myanimelist.net/users.php"

list_of_countries = ["Italy", "USA", "Germany", "Japan", "Brasil", "Russia",
                     "Greece", "Saudi Arabia", "Egypt", "England", "Mexico"]

for country in list_of_countries[8:len(list_of_countries)]:
    print country
    # search by country, age and gender don't care
    country_url = url + "?q=&loc=" + country + "&agelow=0&agehigh=0&g="
    print country_url
    # try to connect until 10 attempts
    attempts_1 = 0
    while attempts_1 < 10:
        try:
            response_1 = urllib2.urlopen(country_url)
            break
        except urllib2.HTTPError, e:
            attempts_1 += 1

    # read
    html_1 = response_1.read()

    search = re.findall('''href=["'](/profile/[0-9a-zA-Z|_\-]+)["']''', html_1, re.UNICODE)
    users = list()
    # add users to main list
    for t in range(len(search) / 2):
        users.append(search[t * 2])
    print users
    # users i retrieved at the moment
    current_users = 24
    # users in each page
    users_per_page = 24
    # num pages to crawl
    num_pages = 5

    # retrieve 120 users
    while current_users <= users_per_page*num_pages:
        country_url = url + "?q=&loc=" + country + "&agelow=0&agehigh=0&g=&show="+str(current_users)
        print country_url
        # try to connect until 10 attempts
        attempts_1 = 0
        while attempts_1 < 10:
            try:
                response_1 = urllib2.urlopen(country_url)
                break
            except urllib2.HTTPError, e:
                attempts_1 += 1

        # read
        html_1 = response_1.read()

        users_2 = re.findall('''href=["'](/profile/[0-9a-zA-Z|_\-]+)["']''', html_1, re.UNICODE)
        print users_2
        # add users to main list
        for t in range(len(users_2)/2):
            users.append(users_2[t*2])
        current_users += users_per_page

    print users
    # if we want to write to a local file

    for user in users:
        print user
        # file to be written to
        file = "D:\\users\\" + user[9: len(user)] + ".html"

        attempts_2 = 0
        while attempts_2 < 10:
            try:
                user_profile = urllib2.urlopen("https://myanimelist.net/animelist/" + user[9: len(user)])
                break
            except urllib2.HTTPError, e:
                print attempts_2
                attempts_2 += 1

        user_profile_html = user_profile.read()

        # open the file for writing
        fh = open(file, "w")

        # write to file
        fh.write(user_profile_html)
        fh.close()


def check_json_presence(username):
    """
    This function is used to select only users with an anime list easy to process.
    :param username: self-explaining
    :return: True if the html code of user's anime list has a json in it, or False otherwise.
    """
    anime_list = "https://myanimelist.net/animelist/"+username
    html_page = urllib2.urlopen(anime_list)
    soup = BeautifulSoup(html_page, 'html.parser')
    json_table = soup.find_all('table', attrs={'data-items': True})
    return json_table is not None


