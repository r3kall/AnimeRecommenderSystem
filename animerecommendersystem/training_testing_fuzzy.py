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
    model = NearestNeighbors(n_neighbors=k+1, metric='correlation',
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
                 1 - distances[i][j + 1])
            n_list.append(t)
        neighbors[user] = n_list

    return neighbors


def rmse(user_item_matrix, neighbors):

    relevant_counter = 0  # items with rate != 0 and that exist in the neighbors
    total_counter = 0  # items with rate != 0
    mae_list = []

    for user in user_item_matrix.keys()[:100]:
        for item_id, attributes in user_item_matrix[user]['list'].iteritems():
            if attributes['rate'] != 0:
                total_counter += 1
                pred_num = 0.
                pred_dem = 0.

                for n in neighbors[user]:
                    neigh_rate = user_item_matrix[n[0]]['list'].get(item_id)
                    if neigh_rate is not None:
                        pred_num += n[1] * (
                            neigh_rate['rate'] - user_item_matrix[n[0]]['mean_rate']
                        )
                        pred_dem += n[1]

                if pred_dem == 0:
                    print "\nNo item in neigh"
                    prediction = max(user_item_matrix[user]['mean_rate'], 1.)
                else:
                    prediction = max(user_item_matrix[user]['mean_rate'] + (pred_num / pred_dem), 1.)
                    relevant_counter += 1

                mae_list.append(np.abs(prediction - attributes['rate']))
                print "prediction:  %f \t true:  %d" % (prediction, attributes['rate'])

    print "\nTotal counter: %d" % total_counter
    print "Relevant counter: %d" % relevant_counter
    print "Not found items: %d\n" % (total_counter - relevant_counter)
    return mae_list


def fuzzy_k_fold_rmse(c=40):
    """Perform k-fold cross validation, with k=5"""

    # these are the same for all iterations
    item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()
    print "Generating Item-Cluster matrix..."
    t0 = time.time()
    item_cluster = item_cluster_matrix(item_feature, c)
    print "Time to compute Item-Cluster matrix with %d clusters:  %f" % (
        c, time.time() - t0
    )

    for i in range(1):
        trn_filename = os.path.join(definitions.FILE_DIR,
                                    "user_item_train_"+str(i)+".json")
        tst_filename = os.path.join(definitions.FILE_DIR,
                                    "user_item_test_"+str(i)+".json")

        trn_user_item = read_user_item_json(trn_filename)
        # tst_user_item = read_user_item_json(tst_filename)

        print "Start building user-cluster matrix"
        trn_user_cluster_dict, trn_user_cluster_matrix, trn_user_cluster_indices = \
            build_user_cluster_matrix(trn_user_item, item_cluster, id_to_pos)

        neighs = k_neighbors(trn_user_cluster_matrix,
                             trn_user_cluster_indices,
                             30)
        trn_rmse = rmse(trn_user_item, neighs)
        print np.mean(trn_rmse)


if __name__ == '__main__':
    fuzzy_k_fold_rmse()
