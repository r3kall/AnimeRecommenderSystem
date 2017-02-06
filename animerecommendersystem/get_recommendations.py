from sklearn.neighbors import NearestNeighbors

from user_cluster_matrix import read_user_item_json
from bucket_sort_anime import sort_list

import numpy as np
import definitions

NUM_NEIGHBORS = 5


def get_neighbors(user_name, user_cluster_dict,
                             user_cluster_matrix,
                             user_cluster_indices):
    """
    :param user_name:
    :param user_cluster_matrix:
    :param user_cluster_indices:
    :return:
    """
    neigh = NearestNeighbors(n_neighbors=NUM_NEIGHBORS)
    neigh.fit(user_cluster_matrix)

    vector = user_cluster_dict[user_name]
    distances, indices = neigh.kneighbors(vector.reshape(1, -1))

    # print distances
    # print indices

    nearest_neighbors_list = list()
    for i in indices[0][1:]:
        nearest_neighbors_list.append(user_cluster_indices[i])

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


def get_recomm_from_user(k, neighbor_list, recom_list, user_anime_list):
    """
    :param user_item: dictionary of anime watched by users
    :param num_recom: number of recommendations we want to take from this user
    :param neigh: current user we want to take recommendations from
    :param anime_list: list of recommendations collected to far (we want to avoid duplicates)
    :return: a new list L such that L contains anime_list and (hopefully) other recommendations.
    """
    new_list = recom_list
    # Sort it in descending order
    neighbor_sorted_list = sort_list(neighbor_list)

    for possible_recommendation in neighbor_sorted_list:
        # Check whether it is contained into anime_list
        if (possible_recommendation not in recom_list) and \
                (possible_recommendation not in user_anime_list):
            k -= 1
            new_list.append(possible_recommendation)

        if k == 0:
            return new_list, k

    # We arrive here only if the neighbor has not enough anime to suggest.
    return new_list, k


def get_recomm(user_name, user_item_matrix, k=10, exclude=True):
    """
    :param user_name: Name of the user we want to give suggetions to
    :param user_item_matrix: read from file computed in user_scraping.py
    :param exlude: if True, exlude all anime seen by the user, otherwise pass an empty list.
    :return: a list of animes that could (possibly) be interesting to him/her
    """
    # read from files computed in user_cluster_matrix.py
    user_cluster_dict = np.load(definitions.USER_CLUSTER_DICT).item()
    user_cluster_matrix = np.load(definitions.USER_CLUSTER_MATRIX)
    user_cluster_indices = np.load(definitions.USER_CLUSTER_INDICES).item()

    # Invoke kNN on the matrix to get neighbors
    neighbors_list = get_neighbors(user_name, user_cluster_dict,
                                              user_cluster_matrix,
                                              user_cluster_indices)

    if exclude:
        user_anime_list = user_item_matrix[user_name].keys()
    else:
        user_anime_list = list()

    # For each neighbor, take some anime
    recom_list = list()
    # TODO cycle on recomm tentatives --> 2 cases
    for neigh in neighbors_list:
        neighbor_list = user_item_matrix[neigh]
        recom_list, k = get_recomm_from_user(k, neighbor_list,
                                             recom_list, user_anime_list)
        if k == 0:
            break

    # Return them
    return recom_list

if __name__ == '__main__':
    user_item = read_user_item_json()
    usernames = user_item.keys()

    for user in usernames[0:1]:
        user_list = user_item[user]
        readable_user_list = user_list.keys()
        recomm = get_recomm(user, user_item, exclude=True)

    print '\n** recommendations **'
    print recomm

    print '\n** intersection with user list **'
    it = []
    for e in recomm:
        if e in readable_user_list:
            it.append(e)
    print it