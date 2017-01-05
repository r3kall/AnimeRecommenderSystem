"""
download-dataset-anime.py

This script downloads and creates the dataset consisting of all animes from
MyAnimeList site, and proceeds in two phases:

    1)  Download all the links related to an anime page.

    2)  Scrape and store all the information from each anime page
        in a JSON record.
"""
import io
import time
import urllib2
from bs4 import BeautifulSoup

import definitions


BASE_LIST_URL = "https://myanimelist.net/topanime.php?limit="


def download_links():
    """
    This function download all the anime links and store them in a txt file.
    """
    print "\nStart to download links..."
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


if __name__ == '__main__':
    print __doc__
    print download_links.__name__ + ":" + download_links.__doc__
    download_links()
