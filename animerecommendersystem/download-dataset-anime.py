"""
download-dataset-anime.py

This script downloads and creates the dataset consisting of all animes from
MyAnimeList site, and proceeds in two phases:

    1)  Download all the links related to an anime page.

    2)  Scrape and store all the information from each anime page
        in a JSON record.
"""
import io
import os
import time
import urllib2
from bs4 import BeautifulSoup

import definitions

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
    with io.open(definitions.LINKS_FILE, 'w', encoding='utf-8') as f:
        fifty_counter = 0
        while True:
            time.sleep(0.5)
            req = urllib2.Request(BASE_LIST_URL + str(fifty_counter))
            try:
                response = urllib2.urlopen(req)
                page = response.read()
                soup = BeautifulSoup(page, 'html.parser')

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
    counter = 0

    with io.open(definitions.LINKS_FILE, 'r', encoding='utf-8') as links:
        # read from the link file
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
                content = response.read().decode('utf-8')
                # decode content in unicode (needed)
                with io.open(definitions.HTML_DIR + '/' + title_tag + '.html',
                             'w', encoding='utf-8') as df:
                    df.write(content)  # save the HTML page

            except urllib2.HTTPError as e:
                raise Exception("HTML download error, code  %s") % str(e.code)

    t1 = time.time() - t0
    print "Time to download HTML pages:  %s seconds" % str(t1)


def scrape_single_page(filename):
    """
    This function scrape a single anime page from the given URL.

    :param url: URL of the anime page
    :return: dictionary of attributes
    """
    anime_id = int(filename.split('/')[-1][:-5])
    with io.open(filename, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

        title = soup.find('span', {'itemprop': 'name'})
        if title is None:
            raise Exception("Title not found")
        else:
            title = title.text

        img_link = soup.find('img', class_='ac', itemprop='image')
        if img_link is None:
            raise Exception("Image link not found")
        else:
            img_link = img_link['src']

        types = soup.find('a',
                          href=lambda value: value and value.startswith(
                          'https://myanimelist.net/topanime.php?type'))
        if types is None:
            raise Exception("Type not found")
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
        if len(genres) > 0:
            gen_list = list()
            for g in genres:
                gen_list.append(g.text)
        else:
            raise Exception("Genres not found")

        rating = soup.find(text='Rating:')
        if rating is None:
            raise Exception("Rating not found")
        else:
            rating = rating.next.strip()

        score = soup.find('div', class_='fl-l score')
        if score is None:
            raise Exception("Score not found")
        else:
            score = float(score.text)

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


if __name__ == '__main__':
    # print __doc__
    # print download_links.__name__ + ":" + download_links.__doc__
    # download_links()  # download all the links

    print download_html_files.__name__ + ":" + download_html_files.__doc__
    download_html_files()  # download all the HTML pages

    n_of_html_pages = len(os.listdir(definitions.HTML_DIR))
    print "Number of HTML pages:  %d" % n_of_html_pages
