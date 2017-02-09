"""
training_testing_fuzzy.py

This file will perform training and testing on the recommendation system based
on fuzzy clustering. In other words, we want to tune our system in order to get
results with the highest quality.
"""

import numpy as np

from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import correlation


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
    rmse_num = 0.
    relevant_counter = 0  # items with rate != 0 and that exist in the neighbors
    total_counter = 0  # items with rate != and that not exist in the neighbors
    for user in user_item_matrix.keys():
        for item_id, attributes in user_item_matrix['list'].iteritems():
            if attributes['rate'] != 0:
                pred_num = 0.
                pred_dem = 0.
                total_counter += 1
                for n in neighbors[user]:
                    neigh_rate = user_item_matrix[n[0]]['list'].get(item_id)
                    if neigh_rate is not None:
                        pred_num += n[1] * (
                            neigh_rate - user_item_matrix[n[0]]['mean_rate']
                        )
                        pred_dem += n[1]
                        relevant_counter += 1
                prediction = user_item_matrix[user]['mean_rate'] + (pred_num / pred_dem)
                rmse_num += ((prediction - attributes['rate']) ** 2)
    return np.sqrt(rmse_num / relevant_counter)




from user_cluster_matrix import read_user_item_json, build_user_cluster_matrix
from item_cluster_matrix import build_item_feature_matrix, item_cluster_matrix

user_item = read_user_item_json()

item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()
item_cluster = item_cluster_matrix(item_feature, 10)

print "Start building user-cluster matrix"
user_cluster_dict, user_cluster_matrix, user_cluster_indices = \
    build_user_cluster_matrix(user_item, item_cluster, id_to_pos)

neigh = k_neighbors(user_cluster_matrix, user_cluster_indices, 5)


def k_fold_rmse():
    """Perform k-fold cross validation, with k=5"""

    # these are the same for all iterations
    item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()
    item_cluster = item_cluster_matrix(item_feature, 10)

    for i in range(5):
        trn_filename = "user_item_train_"+str(i)+".json"
        tst_filename = "user_item_test_"+str(i)+".json"

        trn_user_item = read_user_item_json(trn_filename)
        tst_user_item = read_user_item_json(tst_filename)

        print "Start building user-cluster matrix"
        trn_user_cluster_dict, trn_user_cluster_matrix, trn_user_cluster_indices = \
            build_user_cluster_matrix(trn_user_item, item_cluster, id_to_pos)

        neighs = k_neighbors(trn_user_cluster_matrix,
                             trn_user_cluster_indices,
                             5)
        trn_rmse = rmse(trn_user_item, neighs)
        print trn_rmse