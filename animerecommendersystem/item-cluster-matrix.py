"""
item-cluster-matrix.py

This script build from an item-feature representation, a matrix of dimension M x C, with M = number of anime and
C = number of clusters, in an item-cluster representation, using the Fuzzy C Means algorithm.

    1) Build up the item-feature matrix.
    2) Create the item-cluster matrix.
"""

import numpy as np
import skfuzzy as fuzz
import json

import definitions


def read_item_feature_json():
    """
    Read the json file and return a dictionary representation of the item-feature matrix.
    :return:  dictionary with pairs (anime id, list of binary feature)
    """
    with open(definitions.JSON_FILE, 'r') as fp:
        d = json.load(fp)

    if d is not None:
        return d
    return None


def build_item_feature_matrix():
    """
    Phase 1: build up the item-feature matrix.
    :return: numpy matrix (M x C), dictionary of the id indices
    """
    d = read_item_feature_json()  # get the dictionary representation
    indices = dict()

    list_of_list = []
    counter = 0
    for k, v in d.iteritems():
        list_of_list.append(v)
        indices[counter] = int(k)
        counter += 1

    return np.array(list_of_list, dtype=np.int8), indices


def item_cluster_matrix(item_feature_matrix, num_of_cluster, max_iter):
    """
    This function perform Fuzzy C Means on the item-feature matrix and return the item-cluster matrix.
    """
    data = item_feature_matrix.T
    seed = np.random.seed(123)

    cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
        data, num_of_cluster, 2, error=0.005, maxiter=max_iter, seed=seed
    )

    return u.T


m, indices = build_item_feature_matrix()
fm = item_cluster_matrix(m, 100, 1000)
print fm.shape
print fm[0, :]
# print sum(fm[0, :])
print indices[0]

