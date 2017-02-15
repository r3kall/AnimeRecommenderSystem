import time

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D

import sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))

from cmeans import cmeans
from animerecommendersystem.data_processing.item_cluster_matrix import build_item_feature_matrix

X, ind = build_item_feature_matrix()
dim = X.shape[1]
alldata = X.T

ncenters = 20

t0 = time.time()
cntr, u, u0, d, jm, p, fpc = cmeans(
    alldata, ncenters, 2, error=0.0001, maxiter=1000, init=None
)
t1 = time.time()

print "Time to performs fuzzy clustering with %d cluster" \
      " of %d-dimensional data:  %f s" % (ncenters, dim, t1 - t0)

print "=" * 71

model = PCA(n_components=3)
newX = model.fit_transform(X)
dim = newX.shape[1]

# colors definition
dc = dict()
for name, chex in matplotlib.colors.cnames.iteritems():
    dc[name] = chex

colors = list()
for c in dc.itervalues():
    colors.append(c)

fig1 = plt.figure()
ax1 = fig1.add_subplot(111, projection='3d')

t0 = time.time()
cntr, u, u0, d, jm, p, fpc = cmeans(
    newX.T, ncenters, 2, error=0.0001, maxiter=1000, init=None
)
t1 = time.time()

print "Time to performs fuzzy clustering with %d cluster" \
      " of %d-dimensional data:  %f s" % (ncenters, dim, t1 - t0)

cluster_membership = np.argmax(u, axis=0)
for j in range(ncenters):
    ax1.scatter(newX[:, 0][cluster_membership == j],
                newX[:, 1][cluster_membership == j],
                newX[:, 2][cluster_membership == j],
                color=colors[j])

ax1.set_title("Clustering")
plt.show()
