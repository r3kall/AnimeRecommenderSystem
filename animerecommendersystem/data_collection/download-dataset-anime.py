"""
download-dataset-anime.py

This script downloads and creates the dataset consisting of all animes from
MyAnimeList site, and proceeds in three phases:

    1)  Download all the links related to an anime page.

    2)  Download locally all the HTML pages of the anime.

    3)  Scrape and store all the information from each anime page
        in a JSON record.
"""
import io
import os
import time
import json
import urllib2
import argparse
from bs4 import BeautifulSoup

from animerecommendersystem.utils import definitions

if not os.path.exists(definitions.FILE_DIR):
    os.makedirs(definitions.FILE_DIR)
if not os.path.exists(definitions.HTML_DIR):
    os.makedirs(definitions.HTML_DIR)


BASE_LIST_URL = "https://myanimelist.net/topanime.php?limit="


def download_links():
    """
    This function download all the anime links and store them in a txt file.
    """
    print "\nStarting download links..."
    t0 = time.time()
    # open the link file in write mode
    with io.open(definitions.LINKS_FILE, 'w', encoding='utf-8') as f:
        fifty_counter = 0  # url page counter (0 ... 50 ... 100 ... ecc)
        while True:  # until counter ends and an exception is raised
            time.sleep(0.5)  # prevents bad intentions
            req = urllib2.Request(BASE_LIST_URL + str(fifty_counter))
            try:
                response = urllib2.urlopen(req)
                page = response.read()
                soup = BeautifulSoup(page, 'html.parser')

                # get all anime page links
                list_of_links = soup.find_all(
                    "a",
                    class_='hoverinfo_trigger fl-l ml12 mr8'
                )

                fifty_counter += 50

                for tag in list_of_links:
                    link = tag.get("href", None)
                    if link is not None:
                        f.write(link + "\n")

            except urllib2.HTTPError as err1:
                print err1.code
                break
            except urllib2.URLError as err2:
                print err2.reason
                break

    t1 = time.time() - t0
    print "Time to download links:  %s seconds" % str(t1)


def download_html_files():
    """
    This function download the anime html pages from the link list.
    """
    print "\nStarting download HTML files..."
    t0 = time.time()
    counter = 0  # only for status monitoring reasons

    # read from the link file
    with io.open(definitions.LINKS_FILE, 'r', encoding='utf-8') as links:
        for url in links:
            counter += 1
            if counter % 1000 == 0:
                print "Reached link number %d" % counter
            # time.sleep(0.5)  # sleep to avoid misunderstanding with server
            url = url.rstrip('\n')  # strip the newline from url
            title_tag = url.split('/')[-2]  # get the title
            try:
                url = url.encode('ascii', 'ignore')  # encode the url in ASCII
                response = urllib2.urlopen(url)
                # decode content in unicode (needed)
                content = response.read().decode('utf-8', 'ignore')
                html_file = os.path.join(definitions.HTML_DIR,
                                         title_tag + '.html')
                with io.open(html_file, 'w', encoding='utf-8') as df:
                    df.write(content)  # save the HTML page

            except urllib2.HTTPError as e:
                raise Exception("HTML download error, code  %s") % str(e.code)

    t1 = time.time() - t0
    print "Time to download HTML pages:  %s seconds" % str(t1)


def scrape_single_page(filename, name):
    """
    This function scrape a single anime page.

    :param filename: filename of the anime page
    :return: dictionary of relevant attributes
    """
    # anime_id = int(filename.split('/')[-1][:-5])  # get ID from the filename
    anime_id = int(name.split('.')[0])
    with io.open(filename, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

        title = soup.find('span', {'itemprop': 'name'})
        if title is None:
            raise Exception("Title not found")
        else:
            title = title.text

        img_link = soup.find('img', class_='ac', itemprop='image')
        if img_link is None:
            img_link = None
        else:
            img_link = img_link['src']

        types = soup.find('a',
                          href=lambda value: value and value.startswith(
                          'https://myanimelist.net/topanime.php?type'))
        if types is None:
            types = None
        else:
            types = types.text

        status = soup.find_all(text='Status:')
        if len(status) > 0:
            status = status[1].next.strip()
        else:
            raise Exception("Status not found")

        genres = soup.find_all('a',
                               href=lambda value: value and value.startswith(
                               '/anime/genre/'))
        gen_list = list()
        for g in genres:
            gen_list.append(g.text)

        rating = soup.find(text='Rating:')
        if rating is None:
            raise Exception("Rating not found")
        else:
            rating = rating.next.strip()
            rating = rating.split(' ')[0]

        score = soup.find('div', class_='fl-l score')
        if score is None:
            raise Exception("Score not found")
        else:
            score = score.text

        score_count = soup.find('div', class_='fl-l score')
        if score_count is None:
            raise Exception("Score Count not found")
        else:
            score_count = int(score_count['data-user'].split(' ')[0].replace(',', ''))

        popularity = soup.find('span', {'class': 'numbers popularity'})
        if popularity is None:
            raise Exception("Popularity rank not found")
        else:
            popularity = popularity.find('strong')
            popularity = int(popularity.text[1:])

        return {'id': anime_id, 'title': title, 'image_link': img_link,
                'type': types, 'status': status, 'genres': gen_list,
                'score_count': score_count, 'popularity': popularity,
                'rating': rating, 'score': score}


def convert_item_features(item_dictionary):
    """
    This function convert item raw information to proper data.

    :param item_dictionary:  a dictionary with raw item data
    :return: anime id , list of binary feature
    """

    def type_switch_wrapper(argument):
        """this get the type and return a binary (exlusive) list"""
        switcher = {
            "TV": [1, 0, 0, 0, 0, 0],
            "OVA": [0, 1, 0, 0, 0, 0],
            "Movie": [0, 0, 1, 0, 0, 0],
            "Special": [0, 0, 0, 1, 0, 0],
            "ONA": [0, 0, 0, 0, 1, 0],
            "Music": [0, 0, 0, 0, 0, 1]
        }
        return switcher.get(argument, [0, 0, 0, 0, 0, 0])

    def genre_switcher_wrapper(list_of_genres):
        """this get the list of genres and return a binary list"""
        genres = [0] * 45
        indices = {
            "Action": 0,
            "Adventure": 1,
            "Cars": 2,
            "Comedy": 3,
            "Dementia": 4,
            "Demons": 5,
            "Mystery": 6,
            "Drama": 7,
            "Ecchi": 10,
            "Fantasy": 11,
            "Game": 12,
            "Historical": 13,
            "Horror": 14,
            "Kids": 15,
            "Magic": 16,
            "Martial Arts": 17,
            "Mecha": 18,
            "Music": 19,
            "Parody": 20,
            "Samurai": 21,
            "Romance": 22,
            "School": 23,
            "Sci-Fi": 24,
            "Shoujo": 25,
            "Shoujo Ai": 26,
            "Shounen": 27,
            "Shounen Ai": 28,
            "Space": 29,
            "Sports": 30,
            "Super Power": 31,
            "Vampire": 32,
            "Yaoi": 33,
            "Yuri": 34,
            "Harem": 35,
            "Slice of Life": 36,
            "Supernatural": 37,
            "Military": 38,
            "Police": 39,
            "psychological": 40,
            "Thriller": 41,
            "Seinen": 42,
            "Josei": 43,
            "Hentai": 44
        }

        for g in list_of_genres:
            i = indices.get(g, None)
            if i is not None:
                genres[i] = 1

        return genres

    def demo_switcher_wrapper(arguement):
        switcher = {
            "G": [1, 0, 0, 0, 0, 0],
            "PG": [0, 1, 0, 0, 0, 0],
            "PG-13": [0, 0, 1, 0, 0, 0],
            "R": [0, 0, 0, 1, 0, 0],
            "R+": [0, 0, 0, 0, 1, 0],
            "Rx": [0, 0, 0, 0, 0, 1]
        }
        return switcher.get(arguement, [0, 0, 0, 0, 0, 0])

    l1 = type_switch_wrapper(item_dictionary['type'])
    l2 = genre_switcher_wrapper(item_dictionary['genres'])
    l3 = demo_switcher_wrapper(item_dictionary['rating'])

    res = l1 + l2 + l3

    return item_dictionary['id'], res


def create_item_feature_json():
    """
    This function create and save a JSON representation of
    the item-feature matrix.
    """
    d = dict()  # data dictionary that will be saved in JSON
    html_list = os.listdir(definitions.HTML_DIR)

    print "Generating JSON file..."
    t0 = time.time()
    # for each html file in the html folder
    for h in html_list:
        # get raw data
        html_file = os.path.join(definitions.HTML_DIR, h)
        scraped = scrape_single_page(html_file, h)
        id, r = convert_item_features(scraped)  # convert in binary data
        # add the pair (id, list of binary feature) to the dictionary
        d[id] = r

    with open(definitions.JSON_FILE, 'w') as fp:
        j = json.dump(d, fp, sort_keys=True)

    t1 = time.time() - t0
    print "JSON file completed in:  %s" % str(t1)


if __name__ == '__main__':
    print __doc__
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--links", action="store_true",
                       help="download all anime links")
    group.add_argument("-d", "--download", action="store_true",
                       help="download all anime pages")
    group.add_argument("-j", "--json", action="store_true",
                       help="create the json file")

    args = parser.parse_args()

    if args.links:
        download_links()
    elif args.download:
        download_html_files()
    elif args.json:
        create_item_feature_json()
    else:
        print "Warning: run  'python {} --help'  " \
              "to visualize help and usage\n".format(str(__file__))
