"""
online_recommendations.py

Get recommendations for a given user with the fuzzy technique.
"""

import definitions
from training_testing_fuzzy import k_neighbors
from user_cluster_matrix import read_user_item_json, build_user_cluster_matrix
from item_cluster_matrix import build_item_feature_matrix, item_cluster_matrix


def get_recommendations(user_item_matrix, neighbors, username):

    rec_dict = {}
    # find possible reccomandations in the user neighborhood
    for n in neighbors:
        for item_id, attributes in user_item_matrix[n[0]]['list'].iteritems():
            # consider an item only if has positive rate
            if attributes['rate'] >= 6:
                if rec_dict.get(item_id) is None:
                    rec_dict[item_id] = {}
                    rec_dict[item_id]['ranksum'] = float(attributes['rate']) * n[1]
                    rec_dict[item_id]['simsum'] = n[1]
                else:
                    rec_dict[item_id]['ranksum'] += float(attributes['rate']) * n[1]
                    rec_dict[item_id]['simsum'] += n[1]

    # remove items already in the user list
    user_list = user_item_matrix[username]
    for item_id in user_list['list'].iterkeys():
        if item_id in rec_dict.keys():
            rec_dict.pop(item_id)

    # sort per weighted mean
    rec_list = [(k, rec_dict[k]['ranksum'] / rec_dict[k]['simsum']) for k in rec_dict.keys()]
    return sorted(rec_list, key=lambda x: x[1], reverse=True)


def input_loop(c, k, n):
    """
    :param c: number of clusters to use.
    :param k: number of neighbors to consider.
    :param n: number of recommendations to consider.
    :return: list of the top n recommendations.
    """
    # these are the same for all iterations
    user_item = read_user_item_json(definitions.JSON_USER_FILE)
    print "[ Username example:  %s ]" % user_item.keys()[123]
    item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()
    item_cluster = item_cluster_matrix(item_feature, c)

    user_cluster_dict, user_cluster_matrix, user_cluster_indices = build_user_cluster_matrix(
        user_item, item_cluster, id_to_pos
    )

    neighs = k_neighbors(user_cluster_matrix,
                         user_cluster_indices,
                         k)

    username = str(raw_input('Insert username: '))
    r = get_recommendations(user_item, neighs[username], username)
    print r[:n]


if __name__ == '__main__':
    input_loop(61, 20, 30)