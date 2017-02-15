
import os
import time

import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors

from animerecommendersystem.utils import definitions
from animerecommendersystem.data_processing.user_cluster_matrix import read_user_item_json
from animerecommendersystem.data_processing.item_cluster_matrix import build_item_feature_matrix


def build_user_item_sparse_matrix(filename):
    user_item = read_user_item_json(filename)
    item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()

    N = len(user_item.keys())
    M = item_feature.shape[0]

    user_item_sparse = np.zeros((N, M), dtype=np.uint16)
    user_mean = np.zeros(N)
    user_count = 0
    # user_count correspond to the i-th key
    # of the iteration over user_item keys
    for user in user_item.keys():
        sumrank = 0.
        relevant = 0.
        for item_id, values in user_item[user]['list'].iteritems():
            try:
                item_index = id_to_pos[int(item_id)]
            except KeyError:
                continue
            rate = values['rate']
            user_item_sparse[user_count, item_index] = rate
            if rate > 0:
                relevant += 1
                sumrank += rate

        if relevant > 0:
            user_mean[user_count] = sumrank / relevant
        else:
            user_mean[user_count] = 5.5

        user_count += 1

    return user_item_sparse, user_mean


def k_neighbors(sparse_matrix, k):
    # create the k-neighbors unsupervised model
    model = NearestNeighbors(n_neighbors=k+1, metric='cosine',
                             algorithm='brute', leaf_size=30,
                             n_jobs=1)

    model.fit(sparse_matrix)  # train the model

    # compute k-neighbors, returning the index and distance matrices
    distances, indices = model.kneighbors(sparse_matrix,
                                          return_distance=True)

    return distances[:, 1:], indices[:, 1:]


def evaluate(user_item_sparse, neighbors, distances, mean_rates):

    relevant_counter = 0  # items with rate != 0 and that exist in the neighbors
    total_counter = 0  # items with rate != 0
    mae_list = []
    rmse_list = []

    for u in range(user_item_sparse.shape[0]):
        for it in range(user_item_sparse.shape[1]):
            if user_item_sparse[u, it] != 0:
                total_counter += 1
                pred_num = 0.
                pred_dem = 0.

                for n in range(neighbors.shape[1]):
                    neigh_rate = user_item_sparse[neighbors[u, n], it]
                    if neigh_rate > 0:
                        sim = (1. - distances[u, n])
                        pred_num += sim * (
                            neigh_rate - mean_rates[neighbors[u, n]]
                        )
                        pred_dem += sim

                if pred_dem == 0:
                    # print "\nNo item in neigh"
                    # prediction = user_item_matrix[user]['mean_rate']
                    continue
                else:
                    prediction = mean_rates[u] + (pred_num / pred_dem)
                    # prediction = pred_num / pred_dem
                    relevant_counter += 1

                if prediction < 1.:
                    prediction = 1.
                if prediction > 10.:
                    prediction = 10.

                mae_list.append(np.abs(prediction - float(user_item_sparse[u, it])))
                rmse_list.append((prediction - float(user_item_sparse[u, it])) ** 2)
                # print "prediction:  %f \t true:  %d" % (prediction, attributes['rate'])

    not_found_ratio = 1. - (float(relevant_counter) / float(total_counter))
    return np.array(mae_list), np.array(rmse_list), not_found_ratio


def cf_k_fold_rmse(k=5):
    """Perform k-fold cross validation, with k=5"""

    # these are the same for all iterations
    item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()


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

        trn_user_item_sparse, trn_mean_rates = build_user_item_sparse_matrix(trn_filename)

        distances, indices = k_neighbors(trn_user_item_sparse, k)

        trn_mae, trn_rmse, trn_not_found_ratio = evaluate(
            trn_user_item_sparse, indices, distances, trn_mean_rates)

        del trn_user_item_sparse
        del trn_mean_rates
        print "First Evaluation done, iteration %d" % i

        tst_user_item_sparse, tst_mean_rates = build_user_item_sparse_matrix(tst_filename)

        tst_mae, tst_rmse, tst_not_found_ratio = evaluate(
            tst_user_item_sparse, indices, distances, tst_mean_rates)

        del tst_user_item_sparse
        del tst_mean_rates
        print "Second Evaluation done, iteration %d" % i

        trn_mae_list.append(np.mean(trn_mae))
        trn_rmse_list.append(np.sqrt(np.mean(trn_rmse)))
        trn_not_found_ratio_list.append(trn_not_found_ratio)

        tst_mae_list.append(np.mean(tst_mae))
        tst_rmse_list.append(np.sqrt(np.mean(tst_rmse)))
        tst_not_found_ratio_list.append(tst_not_found_ratio)

    return np.mean(trn_mae_list), np.mean(trn_rmse_list), np.mean(trn_not_found_ratio_list), \
           np.mean(tst_mae_list), np.mean(tst_rmse_list), np.mean(tst_not_found_ratio_list)


def compute_evaluation():

    train_mae_list = []
    train_rmse_list = []
    test_mae_list = []
    test_rmse_list = []

    parameters = [3, 5, 7, 10, 30, 50, 75, 100]

    min_rmse = 1000.
    target_k = 0

    for t in parameters:
        print "=" * 71
        print "K = %d" % t
        tr_mae, tr_rmse, tr_ratio, ts_mae, ts_rmse, ts_ratio = cf_k_fold_rmse(k=t)

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

        train_mae_list.append(tr_mae)
        train_rmse_list.append(tr_rmse)
        test_mae_list.append(ts_mae)
        test_rmse_list.append(ts_rmse)

        if ts_rmse < min_rmse:
            min_rmse = ts_rmse
            target_k = t

    print "=" * 71
    print "Min Test RMSE:  %s" % str(min_rmse)
    print "Target K:  %d" % target_k

    return train_mae_list, train_rmse_list, test_mae_list, test_rmse_list, parameters


def draw():
    train_mae_list, train_rmse_list, test_mae_list, test_rmse_list, p = compute_evaluation()

    # plot MAE with fixed clusters
    plt.figure()
    plt.plot(p,
             test_mae_list,
             'r',
             p,
             test_mae_list,
             'rs', lw=2)
    plt.ylabel("MAE")
    plt.xlabel("number of neighbors")
    plt.title("Collaborative Filtering")
    plt.grid(True)

    # plot RMSE with fixed clusters
    plt.figure()
    plt.plot(p,
             test_rmse_list,
             'k',
             p,
             test_rmse_list,
             'ks', lw=2)

    plt.ylabel("RMSE")
    plt.xlabel("number of neighbors")
    plt.title("Collaborative Filtering")
    plt.grid(True)

    plt.show()


if __name__ == '__main__':
    draw()