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


def read_user_item_json(filename):
    """
    Read the json file and return a dictionary representation of the
    user-item matrix.

    :return:  dictionary of users - items
    """
    with open(filename, 'r') as fp:
        d = json.load(fp)

    if d is not None:
        return d
    return None


def ranking(dict_of_attributes):
    """This function return a value depending on values"""
    rate = dict_of_attributes['rate']
    if rate > 0:
        return float(rate), True
    return 0, False


def build_user_cluster_matrix(user_item_matrix,
                              item_cluster_matrix,
                              item_cluster_indices):
    """
    Build up the user-cluster matrix.
    The 'item_cluster_indices' is a dictionary that maps an itemID with the
    position of an item in the 'item_cluster_matrix',
    i.e. "item_cluster_indices[itemID] = position_in_item_cluster_matrix".

    :return: dictionary (N x C)
    """
    user_cluster_dict = dict()  # dictionary (username : cluster vector)

    '''
    This matrix is filled in the order of the users seen, and contains their
    cluster values vector. It is needed to find the nearest neighbors later on,
    and kNN requires a matrix and not a dictionary.
    '''
    N = len(user_item_matrix.keys())
    C = item_cluster_matrix.shape[1]
    user_cluster_matrix = np.empty(shape=(N, C), dtype=np.float64)

    # current position to fill in user_cluster_matrix
    count_position = 0

    '''
    This dictionary is needed to find the username corresponding to an index
    in the user_cluster_matrix.

    So: key->[position in the matrix]
        value->[username of the user whose cluster values are in that position]
    '''
    user_cluster_indices = dict()

    for username in user_item_matrix.keys():
        # initialize an empty vector and zero ranksum
        user_cluster_vector = np.zeros(C, dtype=np.float64)
        ranksum = 0

        # for each item...
        for id, values in user_item_matrix[username]['list'].iteritems():
            try:
                # exception can be raised if we do not have the item
                # in our collection
                pos = item_cluster_indices[int(id)]
            except KeyError:
                continue

            r, valid = ranking(values, user_item_matrix[username]['mean_rate'])
            if valid:
                user_cluster_vector += item_cluster_matrix[pos, :] * r
                ranksum += r

        # weighted vector, avoid possible Nan values
        # user_cluster_vector = np.nan_to_num(user_cluster_vector / ranksum)
        user_cluster_vector = user_cluster_vector / ranksum

        # build user-cluster matrices and dictionaries
        user_cluster_matrix[count_position] = user_cluster_vector
        user_cluster_dict[username] = user_cluster_vector
        user_cluster_indices[count_position] = username

        # go on in the matrix
        count_position += 1

    return user_cluster_dict, user_cluster_matrix, user_cluster_indices
