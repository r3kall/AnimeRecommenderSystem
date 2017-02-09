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

import collaborative_filtering
import math
from user_cluster_matrix import read_user_item_json

STILL_NO_BEST = -1
# Define list of possible parameters
num_neighbors_values = [3, 5, 7]


def compute_rmse(user_animes, recommendations):
    """
    :param user_animes: list of animes for the user we're recommending stuff to.
    :param recommendations: includes only animes seen by user since we are testing
    :return: RMSE computed with predicted rates in recommendations and real rates given by the user on those animes
    """
    sum_squares = 0
    for anime in recommendations:
        sum_squares += math.pow((recommendations[anime]-user_animes[anime]['rate']), 2)
    result = math.sqrt(sum_squares/len(recommendations.keys()))
    return result


def test_cf_system(num_neighbors, user_lists):
    # We want to compute the average RMSE value for this training set. So we need an accumulator
    rmse_sum = 0
    for username in training_user_lists.keys():
        # Pass the parameter we want to test
        recommendations = collaborative_filtering.get_recommendations(username, user_lists, num_neighbors=num_neighbors)
        rmse_sum += compute_rmse(username, recommendations, user_lists[username])
    # Now compute the average, and check whether the new parameter is the new best one.
    avg_rmse = rmse_sum / len(user_lists.keys())
    return avg_rmse


if __name__ == '__main__':
    print "Starting training/testing phase for Collaborative Filtering RS"

    for i in range(0, 5):
        # To decide which parameter is the best one, we need to compare their results.
        current_best_parameter = STILL_NO_BEST
        current_best_rmse = STILL_NO_BEST
        # Get training set and testing set for this particular round
        train_filename = "user_item_train_" + str(i) + ".json"
        test_filename = "user_item_test_" + str(i) + ".json"
        training_user_lists = read_user_item_json(train_filename)
        testing_user_lists = read_user_item_json(test_filename)

        # Call collaborative filtering RS passing the training set. Do it for each possible parameter.
        for n in num_neighbors_values:
            avg_rmse = test_cf_system(n, training_user_lists)
            if current_best_parameter == STILL_NO_BEST or avg_rmse < current_best_rmse:
                current_best_parameter = n
                current_best_rmse = avg_rmse

        print "Best parameter for training set #"+str(i)+" is: "+str(current_best_parameter)
        print "Best RMSE is "+str(current_best_rmse)

        # Take the best parameter and use it on the test set.
        final_rmse = test_cf_system(current_best_parameter, testing_user_lists)
        print "The RMSE value on the testing set is: "+str(final_rmse)
