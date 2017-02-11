"""
item-cluster-matrix.py

This script build from an item-feature representation, a matrix of dimension
M x C, with M = number of anime and C = number of clusters, in an item-cluster
representation, using the Fuzzy C Means algorithm.

    1) Build up the item-feature matrix.
    2) Create the item-cluster matrix.
"""

import numpy as np
import json

import animerecommendersystem.definitions
from animerecommendersystem.fuzzy_clustering.cmeans import cmeans


def read_item_feature_json():
    """
    Read the json file and return a dictionary representation of the
    item-feature matrix.

    :return:  dictionary with pairs (anime id, list of binary feature)
    """
    with open(animerecommendersystem.definitions.JSON_FILE, 'r') as fp:
        d = json.load(fp)

    if d is not None:
        return d
    return None


def build_item_feature_matrix():
    """
    Build up the item-feature matrix.
    :return: numpy matrix (M x F), dictionary of the id indices
    """
    d = read_item_feature_json()  # get the dictionary representation

    pos_to_id = dict()  # mapping of the ID
    id_to_pos = dict()
    list_of_list = []  # binary lists
    counter = 0

    for k, v in d.iteritems():
        list_of_list.append(v)
        id_to_pos[int(k)] = counter
        pos_to_id[counter] = int(k)
        counter += 1

    return np.array(list_of_list, dtype=np.int8), pos_to_id, id_to_pos


def item_cluster_matrix(item_feature_matrix, num_of_cluster,
                        max_iter=1000, error=0.0001):
    """
    This function perform Fuzzy C Means on the item-feature matrix and
    return the item-cluster matrix.

    :return: numpy matrix (M x C) item-cluster
    """
    data = item_feature_matrix.T

    cntr, u, u0, d, jm, p, fpc = cmeans(
        data, num_of_cluster, 1.15, error=error, maxiter=max_iter, seed=123
    )
    print "Clustering Iterations: %d" % p
    return u.T
