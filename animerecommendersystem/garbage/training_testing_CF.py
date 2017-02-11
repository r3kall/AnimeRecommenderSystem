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
    => Split animes in five groups of size 20% of total
    => Select one group as testing set and the other four as training set, in a round-robin fashion.
        => COME SE FA ER TRAINING?
            =>  We focus on the number of neighbors: for each N, for each user U in the training set,
                we run get_recommendations(U, N). Then we take the resulting list R, and we compute RMSE
                on it. Since we'll have one RMSE value for each user, we compute the average RMSE for N.
        => COME SE FA ER TESTING?
            =>  Now we have a RMSE value for each N: we take the value of N with the best RMSE value
                (called N_best), and we apply get_recommendations(U, N_best) for each U in testing_set.

        => At the end, we'll have one RMSE for each testing set: we return the average.
        THE END.

NOTE: testing=True means that we need to apply get_recommendations only on animes watched by the user.
"""
import math
import os

from user_cluster_matrix import read_user_item_json

import collaborative_filtering
import definitions

STILL_NO_BEST = -1
# Define list of possible parameters
num_neighbors_values = [3, 5, 7]


def compute_rmse(user_animes, recommendations):
    """
    :param user_animes: list of animes for the user we're recommending stuff to.
    :param recommendations: includes only animes seen by user since we are testing
    :return: RMSE computed with predicted rates in recommendations and real rates given by the user on those animes
    """
    # First of all, check if the user saw at least one anime. If not, return -1.
    if user_animes.get('list') is None:
        return -1

    sum_squares = 0
    watched_count = 0
    for anime in recommendations:
        if anime in user_animes['list'].keys():
            watched_count += 1
            sum_squares += math.pow((recommendations[anime]-user_animes['list'][anime]['rate']), 2)

    # If the user didn't see any of the proposed animes, we cannot use him for RMSE.
    if watched_count == 0:
        return -1

    result = math.sqrt(sum_squares/len(recommendations.keys()))
    return result


def test_cf_system(num_neighbors, user_lists, user_list_total):
    # We want to compute the average RMSE value for this training set. So we need an accumulator
    rmse_sum = 0
    rmse_count = 0
    for username in training_user_lists.keys()[0:1000]:
        print "          -------------------------------------------------------------"
        print "          Getting recommendations for user "+username
        # Pass the parameter we want to test
        if user_lists[username].get('list') is None:
            print "          Computation not executed for user "+username+" because he/she has no anime."
        else:
            recommendations = collaborative_filtering.get_recommendations(username, user_lists,
                                                                          list_for_recomm=user_list_total,
                                                                          num_neighbors=num_neighbors)
            rmse = compute_rmse(user_list_total[username], recommendations)
            print "          RMSE value for "+username+" is: "+str(rmse)
            if rmse != -1:
                rmse_sum += rmse
                rmse_count += 1
    # Now compute the average, and check whether the new parameter is the new best one.
    if rmse_count != 0:
        avg_rmse = rmse_sum / rmse_count
    else:
        avg_rmse = -1
    return avg_rmse


if __name__ == '__main__':
    print "Starting training/testing phase for Collaborative Filtering RS"
    complete_json_name = train_filename = os.path.join(definitions.FILE_DIR, "user-item.json")

    user_item_complete = read_user_item_json(complete_json_name)

    for i in range(3, 4):
        print "-----------------------------------------------------------------------"
        print "Iteration #"+str(i)
        # To decide which parameter is the best one, we need to compare their results.
        current_best_parameter = STILL_NO_BEST
        current_best_rmse = STILL_NO_BEST
        # Get training set and testing set for this particular round
        train_filename = os.path.join(definitions.FILE_DIR,
                                      "user_item_train_"+str(i)+".json")
        test_filename = os.path.join(definitions.FILE_DIR,
                                     "user_item_test_"+str(i)+".json")
        training_user_lists = read_user_item_json(train_filename)
        testing_user_lists = read_user_item_json(test_filename)

        # Call collaborative filtering RS passing the training set. Do it for each possible parameter.
        for n in num_neighbors_values:
            print "     ------------------------------------------------------------------"
            print "     Trying #neighbors="+str(n)
            avg_rmse = test_cf_system(n, training_user_lists, user_item_complete)
            print "     Average RMSE for n="+str(n)+" is "+str(avg_rmse)
            if current_best_parameter == STILL_NO_BEST or avg_rmse < current_best_rmse:
                current_best_parameter = n
                current_best_rmse = avg_rmse

        print "Best parameter for training set #"+str(i)+" is: "+str(current_best_parameter)
        print "Best RMSE is "+str(current_best_rmse)

        # Take the best parameter and use it on the test set.
        final_rmse = test_cf_system(current_best_parameter, testing_user_lists, user_list_total=user_item_complete)
        print "The RMSE value on the testing set is: "+str(final_rmse)
