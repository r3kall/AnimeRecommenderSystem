from animerecommendersystem.utils import utils_functions
from animerecommendersystem.recommender_systems import FuzzyClusteringRS
from animerecommendersystem.utils import definitions
from animerecommendersystem.data_processing import user_cluster_matrix

import numpy as np
import timeit
import json
import os
import io

BASE_ANIME_LINK = "https://myanimelist.net/anime/"
BASE_USER_LINK = "https://myanimelist.net/animelist/"


def print_html_page(user, recommendations, utility):
    header = u"""<html><head><title>Anime Recommendation System</title></head>"""
    title = u"""<body><b><font size="6"><center>
    Recommendations for user <a href="%s">%s</a>
    </center></font></b>""" % (BASE_USER_LINK + user, user)
    footer = u"""</body></html>"""

    s = ""
    counter = 1
    for r in recommendations:
        t = utility[r[0]]
        link = BASE_ANIME_LINK + str(int(r[0]))

        s += u"""<center>
        <div class="riga">
        <div class="colonna-1">
        <p><img src="%s"></p>
        <br>
        %d - <a href="%s">%s</a>
        </div>
        </div>
        </center>
        <br><br><br>""" % (t[1], counter, link, t[0])
        counter += 1

    message = header + title + s + footer

    f = io.open('rec.html', 'w', encoding='utf-8')
    f.write(message)
    f.close()


if __name__ == '__main__':

    if (not os.path.exists(definitions.USER_CLUSTER_DICT)) or \
            (not os.path.exists(definitions.USER_CLUSTER_MATRIX)) or \
            (not os.path.exists(definitions.USER_CLUSTER_INDICES)):
        user_cluster_matrix.save_user_cluster_matrix()

    users_anime_lists = utils_functions.load_json_file(definitions.JSON_USER_FILE)
    with open(definitions.UTILITY_FILE, 'r') as fp:
        utility = json.load(fp)

    users_clusters_dict = np.load(definitions.USER_CLUSTER_DICT).item()
    users_clusters_matrix = np.load(definitions.USER_CLUSTER_MATRIX)
    users_clusters_indices = np.load(definitions.USER_CLUSTER_INDICES).item()

    fcrs = FuzzyClusteringRS.FuzzyCluseringRS(users_anime_lists, users_clusters_matrix,
                                              users_clusters_dict, users_clusters_indices)

    user = raw_input("Insert username:  ")
    start = timeit.default_timer()
    recommendations = fcrs.get_recommendations(user)
    req_time = timeit.default_timer() - start

    print "------------------------------------------------------------"
    print "Required time to get recommendations = " + str(req_time)
    print recommendations

    print_html_page(user, recommendations, utility)
