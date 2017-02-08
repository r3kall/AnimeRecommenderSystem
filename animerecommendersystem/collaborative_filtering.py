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
import definitions
from user_cluster_matrix import read_user_item_json

from collections import defaultdict
import math

NUM_RECOM = 10
NUM_NEIGHBORS = 5
NEIGHBORS_WEIGHTS = [0.5, 0.4, 0.3, 0.2, 0.1]

# Rate estimations
COMPLETED_RATE = 7
PLANNED_RATE = 7
DROPPED_RATE = 4
WATCHING_RATE = 6
ON_HOLD_RATE = 6


def compute_distance(username1, username2, user_item_matrix):
    # Take the list of animes for each user
    user1_animes = user_item_matrix[username1]
    user2_animes = user_item_matrix[username2]

    distance_numerator = 0
    square_sum_1 = 0
    square_sum_2 = 0

    # Create a set that contains animes watched by at least one of the user.
    total_set_animes = set(user1_animes.keys())
    total_set_animes |= set(user2_animes.keys())
    for anime in total_set_animes:
        watched1 = False
        watched2 = False
        user1_rate = 0
        user2_rate = 0

        if anime in user1_animes.keys():
            watched1 = True
            user1_rate = user1_animes[anime]['rate']
            if user1_rate == 0:
                user1_rate = estimate_rate(user1_animes, anime)

            square_sum_1 += user1_rate*user1_rate

        if anime in user2_animes.keys():
            watched2 = True

            user2_rate = user2_animes[anime]['rate']
            if user2_rate == 0:
                user2_rate = estimate_rate(user2_animes, anime)

            square_sum_2 += user2_rate*user2_rate

        # If both users' lists contain this anime, then we need to increase the similarity
        if watched1 and watched2:
            distance_numerator += user1_rate*user2_rate

    # At the end, use the values collected so far to compute the distance between users.
    distance_denominator = math.sqrt(square_sum_1) * math.sqrt(square_sum_2)
    similarity = distance_numerator/distance_denominator
    distance = 1 - similarity
    return distance


def get_neighbors(username, user_item_matrix):
    """
    Basic idea: compute distance between 'username''s list and all other users, and pick the nearest ones.
    :param username:
    :param user_item_matrix:
    :return:
    """
    distances_dict = defaultdict(float)
    for user2 in user_item_matrix.keys():
        if user2 == username:
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
    distances_dict = sorted(distances_dict, key=distances_dict.get, reverse=True)
    return distances_dict[0:NUM_NEIGHBORS]


def estimate_rate(neighbor_animes, anime):
    # We use a predefined rate according to the anime's state (e.g., DROPPED, COMPLETED, ...)
    anime_state = neighbor_animes[anime]['curr_state']
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


def get_recommendaions(user_name, user_item_matrix, num_recom=NUM_RECOM, exclude=True):
    # Invoke kNN on the matrix to get neighbors
    neighbors_list = get_neighbors(user_name, user_item_matrix)

    aggregate_rates_dict = defaultdict(float)

    i = 0
    for neighbor in neighbors_list:
        neighbor_animes = user_item_matrix[neighbor]
        # For each anime in neighbor_anime, check whether the user watched it. If not, aggregate its rate.
        for anime in neighbor_animes.keys():
            if anime not in user_item_matrix[user_name]:
                # Then, it's good
                neighbor_rate = neighbor_animes[anime]['rate']
                if neighbor_rate == 0:
                    neighbor_rate = estimate_rate(neighbor_animes, anime)

                aggregate_rates_dict[anime] = aggregate_rates_dict.get(anime, 0) + neighbor_rate*NEIGHBORS_WEIGHTS[i]

        i += 1

    # Once we have all possible animes to recommend with the related aggregate weight, we have to pick the best ones.
    aggregate_rates_dict = sorted(aggregate_rates_dict, key=aggregate_rates_dict.get, reverse=True)
    return aggregate_rates_dict[0:num_recom]


if __name__ == '__main__':
    test_user_name = "IsaFrasson"
    print "STARTING"
    user_item_matrix = read_user_item_json()

    starting_time = time.time()
    recommendations = get_recommendaions(test_user_name, user_item_matrix)
    required_time = time.time() - starting_time
    print "Required time: " + str(required_time) + " seconds."
    print "Recommendations: " + str(recommendations)


