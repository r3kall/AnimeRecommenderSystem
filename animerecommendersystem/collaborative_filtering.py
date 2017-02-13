"""
This files offers (i.e., will offer) a recommendation system based on collaborative filtering technique.
1)  Let U be the user we want to give recommendations to, for each user U2 != U we need to compute distance(U, U2) (*)
    and get the top K neighbors. These neighbors should have watched a lot of animes also watched by U,
    giving to them similar rates.
2)  Once we have these K neighbors, we compute an aggregate rate to the animes they watched
    by using the rates given by them (excluding the ones already watched by U, obviously).
    In other words, we try to return as recommendations the animes watched by most of the neighbors
    and with an high rate by (almost) all of them.

(*)HOW DO WE COMPUTE THE DISTANCE BETWEEN U AND U2?
Idea: something similar to cosine similarity
In particolar, for each anime watched by both users, we should compute the product of rates
=> PROBLEM: what if an user didn't rate this anime?
    => We need to estimate this rate.
    => PROBLEM: how?
        => First idea:  use the average of all rates he gave to other animes he watched.
        => Second idea: use the average of all rates he gave to other anime he watched IN THE SAME STATE.
        => Third idea:  use a predefined rate according to the anime state (e.g., we give '4' to it if it is Dropped).
"""

import time
import json
import definitions
from user_cluster_matrix import read_user_item_json
import os

from collections import defaultdict
import math

NUM_RECOM = 10
NUM_NEIGHBORS = 5
NEIGHBORS_WEIGHTS = [0.5, 0.4, 0.3, 0.2, 0.1, 0.1, 0.1]

# Rate estimations
COMPLETED_RATE = 7
PLANNED_RATE = 7
DROPPED_RATE = 4
WATCHING_RATE = 6
ON_HOLD_RATE = 6

# Get near neighbors
AVG_NEAREST_DISTANCE = 0.55
NEAR_RATIO = 1.1

# neighbors = defaultdict(dict)
K = 7


def compute_distance(username1, username2, user_item_matrix):
    # Take the list of animes for each user
    user1_animes = user_item_matrix[username1]
    user2_animes = user_item_matrix[username2]

    distance_numerator = 0
    square_sum_1 = 0
    square_sum_2 = 0

    # Create a set that contains animes watched by at least one of the user.
    total_set_animes = set(user1_animes['list'].keys())
    total_set_animes |= set(user2_animes['list'].keys())
    for anime in total_set_animes:
        watched1 = False
        watched2 = False
        user1_rate = 0
        user2_rate = 0

        if anime in user1_animes['list'].keys():
            watched1 = True
            user1_rate = user1_animes['list'][anime]['rate']
            if user1_rate == 0:
                user1_rate = estimate_rate(user1_animes, anime)

            square_sum_1 += user1_rate*user1_rate

        if anime in user2_animes['list'].keys():
            watched2 = True

            user2_rate = user2_animes['list'][anime]['rate']
            if user2_rate == 0:
                user2_rate = estimate_rate(user2_animes, anime)

            square_sum_2 += user2_rate*user2_rate

        # If both users' lists contain this anime, then we need to increase the similarity
        if watched1 and watched2:
            distance_numerator += user1_rate*user2_rate

    # At the end, use the values collected so far to compute the distance between users.
    distance_denominator = math.sqrt(square_sum_1) * math.sqrt(square_sum_2)
    similarity = distance_numerator/distance_denominator
    distance = 1. - similarity
    return distance


def get_k_neighbors(username, user_item):

    n_dict = opt_neighbors.get(username, {})  # get the possible neighbors from the record

    if len(n_dict.keys()) >= K:
        return n_dict  # if we have all the neighbors, return them

    remaining = K - len(n_dict.keys())  # number of neighbors to get
    print "Remaining neighbors to get:  %d" % remaining
    distances_dict = {}

    how_many_good = 0

    for u in user_item.keys():
        if (u == username) or (u in n_dict.keys()) or (user_item[u].get('list') is None):
            continue

        distance = compute_distance(username, u, user_item)
        distances_dict[u] = distance

        if distance <= AVG_NEAREST_DISTANCE*NEAR_RATIO:
            how_many_good += 1

        if how_many_good == remaining:
            break

    sorted_neighbors = sorted(distances_dict, key=distances_dict.get, reverse=False)[:remaining]

    for n in sorted_neighbors:
        opt_neighbors[username][n] = distances_dict[n]
        if len(opt_neighbors.get(n, {}).keys()) < K:
            opt_neighbors[n][username] = distances_dict[n]

    return opt_neighbors[username]


def save_neighbors_dict():
    filename = os.path.join(definitions.FILE_DIR, 'neighbors.json')
    with open(filename, 'w') as f:
        j = json.dump(opt_neighbors, f)


def get_approx_neighbors(username, user_item_matrix, num_neighbors):
    """
        Basic idea: compute distance between 'username''s list and all other users, and pick the nearest ones.
        => PROBLEM: TOO SLOW.
        => SOLUTION: no need to pick the nearest one, but some near users will be still ok.
    """
    neighbors = defaultdict(float)
    how_many_good = 0
    for user2 in user_item_matrix.keys():
        if user2 == username or user_item_matrix[user2].get('list') is None:
            continue

        distance = compute_distance(username, user2, user_item_matrix)
        neighbors[user2] = distance

        # If this user is close enough to our target, then we take him as a neighbor
        if distance <= AVG_NEAREST_DISTANCE*NEAR_RATIO:
            how_many_good += 1

        if how_many_good == num_neighbors:
            break
    # Sort neighbors according to distance, and return them
    sorted_neighbors = sorted(neighbors, key=neighbors.get, reverse=False)

    # return a dict, so we have also the similarity as info
    res = dict()
    for i in sorted_neighbors[0:num_neighbors]:
        # similarity
        res[i] = 1-neighbors[i]
        #print "Similarity "+str(res[i])
    return res


# Qua non c'e la modifica ma tanto non lo usiamo mai perche fa schifo
def get_neighbors(username, user_item_matrix, num_neighbors):
    """
    Basic idea: compute distance between 'username''s list and all other users, and pick the nearest ones.
    => PROBLEM: TOO SLOW.
    => SOLUTION: no need to pick the nearest one, but some near users will be still ok.
    :param username:
    :param user_item_matrix:
    :param num_neighbors:
    :return:
    """
    distances_dict = defaultdict(float)
    for user2 in user_item_matrix.keys():
        if user2 == username or user_item_matrix[user2].get('list') is None:
            continue

        distance = compute_distance(username, user2, user_item_matrix)
        distances_dict[user2] = distance
        """
        # If the current user is worse than all the previous ones, why save him/her?
        current_max = max(distances_dict.values())
        if distance < current_max or len(distances_dict.keys()) < NUM_NEIGHBORS:
            distances_dict[user2] = compute_distance(username, user2, user_item_matrix)
        """
    # Once we have all distances, sort the dict by value and return a list containing the usernames of the nearest ones.
    sorted_neighbors = sorted(distances_dict, key=distances_dict.get, reverse=False)
    """
    print "Printing distances"
    avg_distance = 0
    for neigh in sorted_neighbors[0:num_neighbors]:
        avg_distance += distances_dict[neigh]
        print "distance: "+str(distances_dict[neigh])
    avg_distance /= num_neighbors
    print "################################ avg_distance="+str(avg_distance)
    """
    return sorted_neighbors[0:num_neighbors]


def estimate_rate(neighbor_animes, anime):
    # We use a predefined rate according to the anime's state (e.g., DROPPED, COMPLETED, ...)
    # TODO Another way to estimate the rate could be based on using the mean_rate
    anime_state = neighbor_animes['list'][anime]['curr_state']
    neighbor_rate = 0
    if anime_state == definitions.COMPLETED:
        neighbor_rate = COMPLETED_RATE
    elif anime_state == definitions.WATCHING:
        neighbor_rate = WATCHING_RATE
    elif anime_state == definitions.DROPPED:
        neighbor_rate = DROPPED_RATE
    elif anime_state == definitions.PLANNED:
        neighbor_rate = PLANNED_RATE
    elif anime_state == definitions.ON_HOLD:
        neighbor_rate = ON_HOLD_RATE

    return neighbor_rate


def get_recommendations(user_name, user_item_matrix, num_neighbors=NUM_NEIGHBORS, weights=NEIGHBORS_WEIGHTS,
                        num_recom=NUM_RECOM, testing=False, approx=True, list_for_recomm=None):

    user_list = user_item_matrix[user_name]

    if approx:
        filename = os.path.join(definitions.FILE_DIR, 'neighbors.json')
        neighbors_dict = read_user_item_json(filename)
    else:
        neighbors_dict = get_neighbors(user_name, user_item_matrix, num_neighbors)

    predictions_rates_dict = defaultdict(float)
    predictions_rates_num_dict = dict()
    predictions_rates_den_dict = dict()

    if list_for_recomm is None:
        list_for_recomm = user_item_matrix

    # i = 0
    for neighbor in neighbors_dict.keys():
        neighbor_animes = list_for_recomm[neighbor]
        # For each anime in neighbor_anime, check whether the user watched it. If not, aggregate its rate.
        if neighbor_animes.get('list') is not None:
            for anime in neighbor_animes['list'].keys():
                # Consider_anime is True if we want to use this anime, False otherwise
                # When do we want to use this anime?
                # 1) The user knows this anime, and we're testing (RMSE works only with known animes)
                # 2) We want to recommend new animes, and the user didn't see it.
                if user_list.get('list') is None:
                    good_for_testing = False
                    good_for_recommend = not testing
                else:
                    good_for_recommend = not testing and anime not in user_list['list'].keys()
                    good_for_testing = testing and anime in user_list['list'].keys()
                if good_for_recommend or good_for_testing:
                    # Then, it's good
                    neighbor_rate = neighbor_animes['list'][anime]['rate']
                    #if neighbor_rate == 0:
                    #    neighbor_rate = estimate_rate(neighbor_animes, anime)
                    # pick similarity from dict
                    if neighbor_rate > 0:
                        predictions_rates_num_dict[anime] = predictions_rates_num_dict.get(anime, 0) + \
                                                        neighbors_dict[neighbor] * \
                                                        (neighbor_rate - user_item_matrix[neighbor]['mean_rate'])
                        predictions_rates_den_dict[anime] = predictions_rates_den_dict.get(anime, 0) + neighbors_dict[neighbor]
        # i += 1
    #print user_item_matrix[user_name]['mean_rate']
    for anime in predictions_rates_num_dict.keys():
        if predictions_rates_den_dict[anime] == 0:
            predictions_rates_dict[anime] = user_item_matrix[user_name]['mean_rate']
        else:
            predictions_rates_dict[anime] = user_item_matrix[user_name]['mean_rate'] + \
                                            (float(predictions_rates_num_dict[anime])/float(predictions_rates_den_dict[anime]))
        if predictions_rates_dict[anime] < 1.:
            predictions_rates_dict[anime] = 3.
        elif predictions_rates_dict[anime] > 10.:
            #print anime
            #print user_name
            #print "BUONGIORNISSIMOOOOO"
            predictions_rates_dict[anime] = 10.
        #else:
            #print "OK"
    # Once we have all possible animes to recommend with the related aggregate weight, we have to pick the best ones.
    sorted_animes = sorted(predictions_rates_dict, key=predictions_rates_dict.get, reverse=True)
    results = dict()
    for anime in sorted_animes[0:num_recom]:
        results[anime] = predictions_rates_dict[anime]
    return results


if __name__ == '__main__':
    '''import os
    print "STARTING"
    filename = os.path.join(definitions.FILE_DIR, 'user_item_train_0.json')
    users_lists = read_user_item_json(filename)
    test_user_names = users_lists.keys()[0:50]
    # test_user_name = 'Lebbing'

    for u in test_user_names:
        print "-" * 71
        print "Username  %s" % str(u)
        print get_k_neighbors(u, users_lists)'''
    filename = os.path.join(definitions.FILE_DIR, "user_item_train_0.json")
    users_lists = read_user_item_json(filename)

    filename = os.path.join(definitions.FILE_DIR, "neighbors.json")
    if os.path.exists(filename):
        opt_neighbors = read_user_item_json(filename)
    else:
        opt_neighbors = defaultdict(dict)

    for u in users_lists.keys()[5:10]:
        get_k_neighbors(u, users_lists)
    save_neighbors_dict()
