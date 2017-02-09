"""
training_testing_fuzzy.py

This file will perform training and testing on the recommendation system based
on fuzzy clustering. In other words, we want to tune our system in order to get
results with the highest quality.
"""
import os
import time
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import correlation

import definitions
from user_cluster_matrix import read_user_item_json, build_user_cluster_matrix
from item_cluster_matrix import build_item_feature_matrix, item_cluster_matrix


def k_neighbors(user_cluster_matrix, user_cluster_indices, k):
    # create the k-neighbors unsupervised model
    model = NearestNeighbors(n_neighbors=k+1, metric='cosine',
                             algorithm='brute', leaf_size=30,
                             n_jobs=1)

    model.fit(user_cluster_matrix)  # train the model

    # compute k-neighbors, returning the index and distance matrices
    distances, indices = model.kneighbors(user_cluster_matrix,
                                          return_distance=True)
    # dictionary of pairs  (username - list of neighbors and similarity)
    neighbors = dict()

    for i in range(indices.shape[0]):
        user = user_cluster_indices[i]
        n_list = list()
        for j in range(indices.shape[1] - 1):
            # a tuple containing names of the neighbors and similarity
            t = (user_cluster_indices[indices[i][j + 1]],
                 1. - distances[i][j + 1])
            n_list.append(t)
        neighbors[user] = n_list

    return neighbors


def evaluate(user_item_matrix, neighbors):

    relevant_counter = 0  # items with rate != 0 and that exist in the neighbors
    total_counter = 0  # items with rate != 0
    mae_list = []
    rmse_list = []

    for user in user_item_matrix.keys()[:1500]:
        for item_id, attributes in user_item_matrix[user]['list'].iteritems():
            if attributes['rate'] != 0:
                total_counter += 1
                pred_num = 0.
                pred_dem = 0.

                for n in neighbors[user]:
                    neigh_rate = user_item_matrix[n[0]]['list'].get(item_id)
                    if neigh_rate is not None:
                        vrate = neigh_rate['rate']
                        if vrate > 0:
                            pred_num += n[1] * (
                                vrate - user_item_matrix[n[0]]['mean_rate']
                            )
                        else:
                            continue
                        pred_dem += n[1]

                if pred_dem == 0:
                    # print "\nNo item in neigh"
                    prediction = user_item_matrix[user]['mean_rate']
                else:
                    prediction = user_item_matrix[user]['mean_rate'] + (pred_num / pred_dem)
                    relevant_counter += 1

                if prediction < 1.:
                    prediction = 3.

                mae_list.append(np.abs(prediction - attributes['rate']))
                rmse_list.append((prediction - attributes['rate']) ** 2)
                # print "prediction:  %f \t true:  %d" % (prediction, attributes['rate'])

    not_found_ratio = 1. - (float(relevant_counter) / float(total_counter))
    return np.array(mae_list), np.array(rmse_list), not_found_ratio


def fuzzy_k_fold_rmse(c=11, k=5):
    """Perform k-fold cross validation, with k=5"""

    # these are the same for all iterations
    item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()
    t0 = time.time()
    item_cluster = item_cluster_matrix(item_feature, c)
    '''
    print "Time to compute Item-Cluster matrix with %d clusters:  %f seconds" % (
        c, time.time() - t0
    )
    '''
    trn_mae_list = []
    trn_rmse_list = []
    trn_not_found_ratio_list = []

    for i in range(2):
        trn_filename = os.path.join(definitions.FILE_DIR,
                                    "user_item_train_"+str(i)+".json")
        tst_filename = os.path.join(definitions.FILE_DIR,
                                    "user_item_test_"+str(i)+".json")

        trn_user_item = read_user_item_json(trn_filename)
        # tst_user_item = read_user_item_json(tst_filename)

        trn_user_cluster_dict, trn_user_cluster_matrix, trn_user_cluster_indices = \
            build_user_cluster_matrix(trn_user_item, item_cluster, id_to_pos)

        neighs = k_neighbors(trn_user_cluster_matrix,
                             trn_user_cluster_indices,
                             k)
        trn_mae, trn_rmse, trn_not_found_ratio = evaluate(trn_user_item, neighs)

        trn_mae_list.append(np.mean(trn_mae))
        trn_rmse_list.append(np.sqrt(np.mean(trn_rmse)))
        trn_not_found_ratio_list.append(trn_not_found_ratio)
    return np.mean(trn_mae_list), np.mean(trn_rmse_list), np.mean(trn_not_found_ratio_list)


if __name__ == '__main__':
    C = 47
    K = 19
    parameters = [(5, K), (5, K+3), (5, K+6),
                  (18, K), (18, K+3), (18, K+6),
                  (C, K), (C, K+3), (C, K+6),
                  (C + 10, K), (C + 10, K + 3), (C + 10, K + 6),
                  (C + 20, K), (C + 20, K+3), (C + 20, K+6),
                  (C + 30, K), (C + 30, K + 3), (C + 30, K + 6),
                  (C + 40, K), (C + 40, K + 3), (C + 40, K + 6),
                  ]

    min_rmse = 1000.
    target_c = 0
    target_k = 0
    for t in parameters:
        print "=" * 71
        mae, rmse, ratio = fuzzy_k_fold_rmse(c=t[0], k=t[1])

        print "C = %d,  K = %d" % (t[0], t[1])
        print "Not Found Ratio:  %f" % ratio
        print "MAE:  %s" % str(mae)
        print "RMSE:  %s" % str(rmse)

        if rmse < min_rmse:
            min_rmse = rmse
            target_c = t[0]
            target_k = t[1]

    print "=" * 71
    print "Min RMSE:  %s" % str(min_rmse)
    print "Target C:  %d" % target_c
    print "Target K:  %d" % target_k
