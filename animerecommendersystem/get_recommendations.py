from sklearn.neighbors import NearestNeighbors

from user_cluster_matrix import read_user_item_json
from bucket_sort_anime import sort_list

import numpy as np
import definitions

NUM_NEIGHBORS = 5


def get_neighbors(user_cluster_dict, user_cluster_matrix, user_matrix_dict_indices, user_name):
    """
    :param user_cluster_dict:
    :param user_cluster_matrix:
    :param user_matrix_dict_indices:
    :param user_name:
    :return:
    """
    neigh = NearestNeighbors(n_neighbors=NUM_NEIGHBORS)
    neigh.fit(user_cluster_matrix)
    vector = user_cluster_dict[user_name]
    distances, indices = neigh.kneighbors(vector.reshape(1, -1))

    # print distances
    # print indices

    nearest_neighbors_list = list()
    for i in indices[0]:
        nearest_neighbors_list.append(user_matrix_dict_indices[i])

    return nearest_neighbors_list


def get_num_recomm(i):
    """
    :param i: Position of the neighbor (e.g., zero = the closest one to our target user)
    :return: number of anime we want to take from this neighbor as a recommendation.
    """
    if i == 0:
        return 4
    elif i == 1:
        return 3
    elif i == 2:
        return 2
    else:
        return 1


def get_recomm_from_user(user_item, num_recom, neigh, anime_list, user_anime_list):
    """
    :param user_item: dictionary of anime watched by users
    :param num_recom: number of recommendations we want to take from this user
    :param neigh: current user we want to take recommendations from
    :param anime_list: list of recommendations collected to far (we want to avoid duplicates)
    :return: a new list L such that L contains anime_list and (hopefully) other recommendations.
    """

    new_list = anime_list
    # Get neigh's list of series
    view_list = user_item[neigh]
    # Sort it in descending order
    sorted_list = sort_list(view_list)
    # Start scrolling the list until you find num_recomm animes that are not in anime_list
    num_added = 0

    for possible_recommendation in sorted_list:
        # possible_recommendation = int(possible_recommendation)
        # Check whether it is contained into anime_list
        if (possible_recommendation not in anime_list) and (possible_recommendation not in user_anime_list):
            num_added += 1
            new_list.append(possible_recommendation)

        if num_added == num_recom:
            return new_list

    # We arrive here only if the neighbor has not enough anime to suggest.
    return new_list


def get_recomm(user_name, exlude=True):
    """
    :param user_name: Name of the user we want to give suggetions to
    :param exlude: if True, exlude all anime seen by the user, otherwise pass an empty list.
    :return: a list of animes that could (possibly) be interesting to him/her
    """
    # read from file computed in user_scraping.py
    user_item = read_user_item_json()

    # read from files computed in user_cluster_matrix.py
    user_cluster_dict = np.load(definitions.USER_CLUSTER_DICT).item()
    user_cluster_matrix = np.load(definitions.USER_CLUSTER_MATRIX)
    user_matrix_dict_indices = np.load(definitions.USER_MATRIX_DICT_INDICES).item()

    # Invoke kNN on the matrix to get neighbors
    neighbors_list = get_neighbors(user_cluster_dict, user_cluster_matrix, user_matrix_dict_indices, user_name)

    # For each neighbor, take some anime
    i = 0
    anime_list = list()
    if exlude:
        user_anime_list = user_item[user_name].keys()
    else:
        user_anime_list = list()

    # TODO cycle on recomm tentatives --> 2 cases
    for neigh in neighbors_list:
        num_recomm = get_num_recomm(i)
        anime_list = get_recomm_from_user(user_item, num_recomm, neigh, anime_list, user_anime_list)
        i += 1

    # Return them
    return anime_list

if __name__ == '__main__':
    print '** get_recommendations.py **'
    user_item = read_user_item_json()
    usernames = user_item.keys()  # list of unicode string that represent user names (id of users)

    for user in usernames[0:100]:
        print user
        user_list = user_item[user]
        readable_user_list = user_list.keys()
        recomm = get_recomm(user, exlude=True)

        print '=============================\n'
        inter = []
        for e in recomm:
            if e in readable_user_list:
                inter.append(e)
        print 'Intersection'
        print inter