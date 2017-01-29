"""
kNN on user cluster matrix
"""
from sklearn.neighbors import NearestNeighbors
from user_cluster_matrix import build_user_cluster_matrix, read_user_item_json, build_item_feature_matrix, item_cluster_matrix


def nearest_neighbors(username):
    """
    :param username:
    :return: nearest neighbors
    """
    vector = user_cluster_dict[username]
    distances, indices = neigh.kneighbors(vector)

    print distances
    print indices

    nearest_neighbors_list = list()
    for i in indices[0]:
        nearest_neighbors_list.append(user_matrix_dict_indices[i])

    print nearest_neighbors_list


if __name__ == '__main__':
    user_item = read_user_item_json()
    item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()
    item_cluster = item_cluster_matrix(item_feature, 10)
    # test with 10 clusters
    print "Start building user-cluster matrix"
    user_cluster_dict, user_cluster_matrix, user_matrix_dict_indices = build_user_cluster_matrix(user_item, item_cluster, id_to_pos)

    # kNN
    neigh = NearestNeighbors(n_neighbors=3)
    neigh.fit(user_cluster_matrix)

    # user to test
    name_user = "_Legna_"
    nearest_neighbors(name_user)


