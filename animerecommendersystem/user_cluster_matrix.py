"""
user_cluster_matrix.py

Starting from the (NxM) user-item matrix (sparse) and the (MxC) item-cluster
matrix, this script creates the (NxC) user-cluster matrix, where each cluster
values per user are computed as:

    for each user u
        for each item i in u
            for each cluster value v in i
                user-cluster += v * ranking(i)

    where ranking(i) is a function that return a value depending on the
    presence of the rank [ranking(i) != 0] and the status of the
    item [status(i)].
"""

import numpy as np
import json

import definitions
from item_cluster_matrix import build_item_feature_matrix, item_cluster_matrix


def read_user_item_json():
    """
        Read the json file and return a dictionary representation of the
        user-item matrix.

        :return:  dictionary of users - items
        """
    with open(definitions.JSON_USER_FILE, 'r') as fp:
        d = json.load(fp)

    if d is not None:
        return d
    return None


def ranking(dict_of_attributes):
    """This function return a value depending on values"""
    rate = dict_of_attributes['rate']
    status = dict_of_attributes['curr_state']

    # An item is valid if it is not in Planned status
    if status != 6:
        if rate > 0:
            return rate, True
        elif status == 4:  # if status = dropped
            return 3, True
        else:
            return 5, True
    return 0, False


def build_user_cluster_matrix(user_item_matrix,
                              item_cluster_matrix, item_cluster_indices):
    """
    Build up the user-cluster matrix.
    The 'item_cluster_indices' is a dictionary that maps an itemID with the
    position of an item in the 'item_cluster_matrix',
    i.e. "item_cluster_indices[itemID] = position_in_item_cluster_matrix"

    :return: dictionary (N x C)
    """
    user_cluster_dict = dict()  # final dictionary (username-cluster vector)

    '''
    This matrix is filled in the order of the users seen, and contains their cluster values vector.
    It is needed to find the nearest neighbors later on, and kNN requires a matrix and not a dictionary
    '''
    user_cluster_matrix = np.empty(shape=(len(user_item_matrix.keys()), item_cluster_matrix.shape[1]), dtype=float)
    # current position to fill in user_cluster_matrix
    count_position = 0

    '''
    This dictionary is needed to find the username corresponding to an index in the user_cluster_matrix
    So: key->[position in the matrix]
        value->[username of the user whose cluster value are in that position in the matrix]
    '''
    user_matrix_dict_indices = dict()

    for username, item_list in user_item_matrix.iteritems():
        # initialize an empty vector and zero ranksum
        user_cluster_vector = np.zeros((item_cluster_matrix.shape[1]),
                                       dtype=np.float64)
        ranksum = 0
        # for each item...
        for id, values in item_list.iteritems():
            try:
                # exception can be raised if we do not have the item
                # in our collection
                pos = item_cluster_indices[int(id)]
            except KeyError:
                continue

            r, valid = ranking(values)  # values depending on values
            if valid:
                user_cluster_vector += item_cluster_matrix[pos, :] * r
                ranksum += r

        # weighted vector, avoid possible Nan values
        user_cluster_vector = np.nan_to_num(user_cluster_vector / ranksum)
        user_cluster_dict[username] = user_cluster_vector

        # build user_cluster_matrix and user_matrix_dict_indices too
        user_cluster_matrix[count_position] = user_cluster_vector
        user_matrix_dict_indices[count_position] = username
        # go on in the matrix
        count_position += 1

    return user_cluster_dict, user_cluster_matrix, user_matrix_dict_indices


if __name__ == '__main__':
    user_item = read_user_item_json()
    item_feature, pos_to_id, id_to_pos = build_item_feature_matrix()
    item_cluster = item_cluster_matrix(item_feature, 10)
    # test with 10 clusters

    print "Start building user-cluster matrix"
    user_cluster_dict, user_cluster_matrix, user_matrix_dict_indices = build_user_cluster_matrix(user_item, item_cluster, id_to_pos)

    # save user_cluster_dict
    np.save(definitions.USER_CLUSTER_DICT, user_cluster_dict)

    # save user_cluster_matrix
    np.save(definitions.USER_CLUSTER_MATRIX, user_cluster_matrix)

    # save user_matrix_dict_indices
    np.save(definitions.USER_MATRIX_DICT_INDICES, user_matrix_dict_indices)

