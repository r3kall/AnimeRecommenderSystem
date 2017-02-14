"""
online_recommendations.py

Get recommendations for a given user with the fuzzy technique.
"""

import definitions
from training_testing_fuzzy import k_neighbors
from user_cluster_matrix import read_user_item_json, build_user_cluster_matrix
from item_cluster_matrix import build_item_feature_matrix, item_cluster_matrix


def get_recommendations(user, user_item_matrix, neighbors):

    rec_list = []
    for item_id, attributes in user_item_matrix[user]['list'].iteritems():
        if attributes['rate'] == 0:
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
                        pred_dem += n[1]

            if pred_dem == 0:
                # print "\nNo item in neigh"
                # prediction = user_item_matrix[user]['mean_rate']
                continue
            else:
                prediction = user_item_matrix[user]['mean_rate'] + (
                pred_num / pred_dem)

            if prediction < 1.:
                prediction = 1.
            if prediction > 10.:
                prediction = 10.

            rec_list.append((item_id, prediction))
    rec_list = sorted(rec_list, key=lambda x: x[1], reverse=True)
    return rec_list


def input_loop(c, k, n):
    """
    :param c: number of clusters to use.
    :param k: number of neighbors to consider.
    :param n: number of recommendations to consider.
    :return: list of the top n recommendations.
    """
    # these are the same for all iterations
    user_item = read_user_item_json(definitions.JSON_USER_FILE)
    item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()
    item_cluster = item_cluster_matrix(item_feature, c)

    user_cluster_dict, user_cluster_matrix, user_cluster_indices = build_user_cluster_matrix(
        user_item, item_cluster, id_to_pos
    )

    neighs = k_neighbors(user_cluster_matrix,
                         user_cluster_indices,
                         k)

    username = str(raw_input('Insert username: '))
    r = get_recommendations(username, user_item, neighs)
    print r[:n]


if __name__ == '__main__':
    input_loop(10, 10, 10)