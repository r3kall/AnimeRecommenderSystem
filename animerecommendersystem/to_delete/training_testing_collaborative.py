"""
This file will perform training and testing on the recommendation system based on collaborative filtering.
In other words, we want to tune our system in order to get results with the highest quality.
=> HOW DO WE TUNE?
    => Our system has three main parameters:
        - Number of neighbors(N)           => Possible values: [3, 5, 7]
        - Weights for each neighbor(W)     => Possible values: (Distance between two weights) [0.1, 0.2, 0.25]
        - Number of recommendations(R)     => Possible values: [10, 12, 15]

We should use k-fold cross validation...
=> ... CHE VOR DI?
    => Split users in five groups of size 20% of total
    => Select one group as testing set and the other four as training set, in a round-robin fashion.
        => COME SE FA ER TRAINING?
            =>  We define a parameter P as a tuple P=[N, W, R], and for each P, for each user U in the training set,
                we run get_recommendations(U, P, testing=True). Then we take the resulting list R, and we compute RMSE
                on it. Since we'll have one RMSE value for each user, we compute the average RMSE for P.
        => COME SE FA ER TESTING?
            =>  Now we have a RMSE value for each P: we take the value of P with the best RMSE value
                (called P_best), and we apply get_recommendations(U, P_best, testing=True) for each U in testing_set.

        => At the end, we'll have one RMSE for each testing set: we return the average.
        THE END.

NOTE: testing=True means that we need to apply get_recommendations only on animes watched by the user.
"""

import math
from animerecommendersystem.user_cluster_matrix import read_user_item_json
from collaborative_filtering import get_recommendations
import numpy as np

NUMBER_NEIGHBORS = [3, 5, 7]
NEIGHBORS_WEIGHTS = [0.1, 0.2, 0.25]
NUMBER_RECOMMENDATIONS = [10, 12, 15]

TESTING_SIZE = 0.2


def split(user_item_matrix, num_permutation):
    """
    :param user_item_matrix:
    :param num_permutation:
    :return: two user_item matrices, one for testing and the other one for training.
    """
    block_size = int(len(user_item_matrix.keys())*TESTING_SIZE)   # 1973 using the json of size 9868
    starting_point = block_size*num_permutation
    ending_point = starting_point+block_size
    training_user_item = {}
    testing_user_item = {}

    # Get all users in testing set
    for user in user_item_matrix.keys()[starting_point: ending_point]:
        testing_user_item[user] = user_item_matrix[user]

    # Get all users in training set
    for user2 in user_item_matrix.keys()[0: starting_point]:
        training_user_item[user2] = user_item_matrix[user2]

    for user2 in user_item_matrix.keys()[ending_point:]:
        training_user_item[user2] = user_item_matrix[user2]

    return training_user_item, testing_user_item


def normalize_rates(recommendations):
    """
    We hope that the user will like our recommendations. Hence, that the user would give a rate at least equal to 6.
    :param recommendations:
    :return: a dictionary with same keys, but normalized values as rates
    """
    max_rate = max(recommendations.values())
    min_rate = min(recommendations.values())
    a = (10-6)/(max_rate-min_rate)
    b = 10 - a*max_rate
    for anime in recommendations.keys():
        recommendations[anime] = a*recommendations[anime]+b

    return recommendations


def compute_rmse(user_animes, recommendations):
    """
    :param user_animes:
    :param recommendations: includes only animes seen by user since we are testing
    :return: RMSE computed with predicted rates in recommendations and real rates given by the user on those animes
    """

    recommendations = normalize_rates(recommendations)
    sum_squares = 0
    for anime in recommendations:
        sum_squares += math.pow((recommendations[anime]-user_animes[anime]['rate']), 2)
    result = math.sqrt(sum_squares/len(recommendations.keys()))
    return result


def get_rmse(user_item_matrix, n, w, r):
    """
    :param user_item_matrix:
    :param n:
    :param w:
    :param r:
    :return: the average value of rmse for this given set of users, and this given tuple of parameters [n, w, r]
    """
    rmse_sum = 0
    weights_list = list()
    for i in range(0, n):
        weights_list.insert(0, (i+1)*w)

    for user in user_item_matrix.keys():
        recommendations = get_recommendations(user, user_item_matrix, num_neighbors=n,
                                              weights=weights_list,
                                              num_recom=r, testing=True)
        rmse_sum += compute_rmse(user_item_matrix[user], recommendations)

    return rmse_sum/len(user_item_matrix.keys())

if __name__ == '__main__':
    users_lists = read_user_item_json()

    # store all remse computed for all testing sets
    test_rmse_dict = dict()

    # K-fold cross validation. At each split one of the 5 partitions of the users becomes testing set, the rest is
    # training.
    for i in range(0, 5):
        print "----------------------------------"
        # parameter i decides which partition we are choosing as test.
        train, test = split(users_lists, i)

        min_rmse_parameter = (0, 0, 0)
        min_rmse = 10

        # train parameters
        for n in NUMBER_NEIGHBORS:
            for w in NEIGHBORS_WEIGHTS:
                for r in NUMBER_RECOMMENDATIONS:
                    print str(n) + " " + str(w) + " " + str(r)
                    rmse_current = get_rmse(train, n, w, r)
                    if rmse_current < min_rmse:
                        min_rmse = rmse_current
                        min_rmse_parameter = (n, w, r)

        # use min rmse parameter to get the rmse of the testing set.
        test_rmse_dict[i] = get_rmse(test, min_rmse_parameter[0], min_rmse_parameter[1], min_rmse_parameter[2])
        print "Split "+str(i) + ": best parameter choice is " + str(min_rmse_parameter)
    average_rmse = np.mean(test_rmse_dict.values())
    print "Average rmse for collaborative filtering recommendation system is "+str(average_rmse)







