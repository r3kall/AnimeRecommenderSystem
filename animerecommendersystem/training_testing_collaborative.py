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


