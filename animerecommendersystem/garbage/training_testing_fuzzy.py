"""
training_testing_fuzzy.py

This file will perform training and testing on the recommendation system based
on fuzzy clustering. In other words, we want to tune our system in order to get
results with the highest quality.
"""
import os

import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import NearestNeighbors
from user_cluster_matrix import read_user_item_json, build_user_cluster_matrix

import definitions
from animerecommendersystem.data_processing.item_cluster_matrix import build_item_feature_matrix, item_cluster_matrix


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

    for user in user_item_matrix.keys():
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
                    # prediction = user_item_matrix[user]['mean_rate']
                    continue
                else:
                    prediction = user_item_matrix[user]['mean_rate'] + (pred_num / pred_dem)
                    relevant_counter += 1

                if prediction < 1.:
                    prediction = 1.

                mae_list.append(np.abs(prediction - attributes['rate']))
                rmse_list.append((prediction - attributes['rate']) ** 2)
                # print "prediction:  %f \t true:  %d" % (prediction, attributes['rate'])

    not_found_ratio = 1. - (float(relevant_counter) / float(total_counter))
    return np.array(mae_list), np.array(rmse_list), not_found_ratio


def fuzzy_k_fold_rmse(c=11, k=5):
    """Perform k-fold cross validation, with k=5"""

    # these are the same for all iterations
    item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()
    item_cluster = item_cluster_matrix(item_feature, c)

    trn_mae_list = []
    trn_rmse_list = []
    trn_not_found_ratio_list = []

    tst_mae_list = []
    tst_rmse_list = []
    tst_not_found_ratio_list = []

    # TODO execute with 5 splits
    for i in range(2):
        trn_filename = os.path.join(definitions.FILE_DIR,
                                    "user_item_train_"+str(i)+".json")
        tst_filename = os.path.join(definitions.FILE_DIR,
                                    "user_item_test_"+str(i)+".json")

        trn_user_item = read_user_item_json(trn_filename)
        tst_user_item = read_user_item_json(tst_filename)

        trn_user_cluster_dict, trn_user_cluster_matrix, trn_user_cluster_indices = \
            build_user_cluster_matrix(trn_user_item, item_cluster, id_to_pos)

        neighs = k_neighbors(trn_user_cluster_matrix,
                             trn_user_cluster_indices,
                             k)

        trn_mae, trn_rmse, trn_not_found_ratio = evaluate(trn_user_item, neighs)
        tst_mae, tst_rmse, tst_not_found_ratio = evaluate(tst_user_item, neighs)

        trn_mae_list.append(np.mean(trn_mae))
        trn_rmse_list.append(np.sqrt(np.mean(trn_rmse)))
        trn_not_found_ratio_list.append(trn_not_found_ratio)

        tst_mae_list.append(np.mean(tst_mae))
        tst_rmse_list.append(np.sqrt(np.mean(tst_rmse)))
        tst_not_found_ratio_list.append(tst_not_found_ratio)

    return np.mean(trn_mae_list), np.mean(trn_rmse_list), np.mean(trn_not_found_ratio_list), \
           np.mean(tst_mae_list), np.mean(tst_rmse_list), np.mean(tst_not_found_ratio_list)


def compute_evaluation(C, K):

    train_mae_list = []
    train_rmse_list = []
    test_mae_list = []
    test_rmse_list = []

    parameters = [
        (C, 10), (C, 20), (C, 30), (C, 50), (C, 70), (C, 85), (C, 100),
        (10, K), (25, K), (50, K), (75, K), (90, K), (100, K), (125, K)
    ]

    min_rmse = 1000.
    target_c = 0
    target_k = 0
    for t in parameters:
        print "=" * 71
        print "C = %d,  K = %d" % (t[0], t[1])
        tr_mae, tr_rmse, tr_ratio, ts_mae, ts_rmse, ts_ratio = fuzzy_k_fold_rmse(c=t[0], k=t[1])

        print "\nTraining Set"
        print "Not Found Ratio:  %f" % tr_ratio
        print "MAE:  %s" % str(tr_mae)
        print "RMSE:  %s" % str(tr_rmse)
        print "\nTest Set"
        print "Not Found Ratio:  %f" % ts_ratio
        print "MAE:  %s" % str(ts_mae)
        print "RMSE:  %s" % str(ts_rmse)
        print "\nMAE Training/Test difference:  %f" % (np.abs(tr_mae - ts_mae))
        print "RMSE Training/Test difference:  %f" % (np.abs(tr_rmse - ts_rmse))

        train_mae_list.append((t[0], t[1], tr_mae))
        train_rmse_list.append((t[0], t[1], tr_rmse))
        test_mae_list.append((t[0], t[1], ts_mae))
        test_rmse_list.append((t[0], t[1], ts_rmse))

        if ts_rmse < min_rmse:
            min_rmse = ts_rmse
            target_c = t[0]
            target_k = t[1]

    print "=" * 71
    print "Min Test RMSE:  %s" % str(min_rmse)
    print "Target C:  %d" % target_c
    print "Target K:  %d" % target_k

    return train_mae_list, train_rmse_list, test_mae_list, test_rmse_list


def draw(C, K):
    train_mae_list, train_rmse_list, test_mae_list, test_rmse_list = compute_evaluation(C, K)

    mae_fixed_clusters_x = []
    mae_fixed_clusters_y = []
    rmse_fixed_clusters_x = []
    rmse_fixed_clusters_y = []

    mae_fixed_neighbors_x = []
    mae_fixed_neighbors_y = []
    rmse_fixed_neighbors_x = []
    rmse_fixed_neighbors_y = []

    for t in sorted(test_mae_list, key=lambda x : x[1]):
        if t[0] == C:
            mae_fixed_clusters_x.append(t[1])
            mae_fixed_clusters_y.append(t[2])
    for t in sorted(test_mae_list, key=lambda x: x[0]):
        if t[1] == K:
            mae_fixed_neighbors_x.append(t[0])
            mae_fixed_neighbors_y.append(t[2])

    for t in sorted(test_rmse_list, key=lambda x: x[1]):
        if t[0] == C:
            rmse_fixed_clusters_x.append(t[1])
            rmse_fixed_clusters_y.append(t[2])
    for t in sorted(test_rmse_list, key=lambda x: x[0]):
        if t[1] == K:
            rmse_fixed_neighbors_x.append(t[0])
            rmse_fixed_neighbors_y.append(t[2])

    # plot MAE with fixed clusters
    plt.figure()
    plt.plot(mae_fixed_clusters_x,
             mae_fixed_clusters_y,
             'r',
             mae_fixed_clusters_x,
             mae_fixed_clusters_y,
             'rs', lw=2)
    plt.ylabel("MAE")
    plt.xlabel("number of neighbors")
    plt.title("MAE with fixed number of fuzzy clusters")
    plt.grid(True)

    # plot RMSE with fixed clusters
    plt.figure()
    plt.plot(rmse_fixed_clusters_x,
             rmse_fixed_clusters_y,
             'k',
             rmse_fixed_clusters_x,
             rmse_fixed_clusters_y,
             'ks', lw=2)

    plt.ylabel("RMSE")
    plt.xlabel("number of neighbors")
    plt.title("RMSE with fixed number of fuzzy clusters")
    plt.grid(True)

    # plot MAE with fixed neighbors
    plt.figure()
    plt.plot(mae_fixed_neighbors_x,
             mae_fixed_neighbors_y,
             'r',
             mae_fixed_neighbors_x,
             mae_fixed_neighbors_y,
             'rs', lw=2)
    plt.ylabel("MAE")
    plt.xlabel("number of clusters")
    plt.title("MAE with fixed number of neighbors")
    plt.grid(True)

    # plot RMSE with fixed neighbors
    plt.figure()
    plt.plot(rmse_fixed_neighbors_x,
             rmse_fixed_neighbors_y,
             'r',
             rmse_fixed_neighbors_x,
             rmse_fixed_neighbors_y,
             'rs', lw=2)
    plt.ylabel("RMSE")
    plt.xlabel("number of clusters")
    plt.title("RMSE with fixed number of neighbors")
    plt.grid(True)

    plt.show()


if __name__ == '__main__':
    draw(60, 50)
