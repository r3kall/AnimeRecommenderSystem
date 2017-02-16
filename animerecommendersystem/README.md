# Anime Recommender System

**Sapienza - Università di Roma** <br/>
*Master of Science in Engineering in Computer Science* <br/>
*Data Mining, a.y. 2016-17* <br/>
---

This is the main folder of the project, and contains all the code, 
divided in packages.

**data_collection**<br/>
This package contains two scripts used to collect our dataset.

**data_processing**<br/>
This package is composed of files that build the data structures
we need.

**fuzzy_clustering**<br/>
The *fuzzy_clustering* package contains the code of the algorithm C-Means 
used by the recommender system based on Fuzzy Clustering.

**recommender_systems**<br/>
Here's where the recommender systems' code is contained.

**testing**<br/>
This package contains two minimal scripts to call the recommender systems and output 
the list of recommendations, also showing the required time to get them.

**evaluation**<br/>
The code used during the tuning part is contained here:
* We perfomed a training phase where we computed the quality of recommendations 
 calculated using values for our parameters 
 (i.e., number of neighbors for Collaborative Filtering, 
 while for Fuzzy Clustering we tuned also the number of clusters we use).
* Then we tested the best parameter (selected using the RMSE measure) on a testing set.

Training and testing was made applying k-fold cross validation. 
We partitioned the dataset into five equal groups, 
and then five times we take one of the groups, we use it as a test set, 
and the other four ones as a training set.

**utils**<br/>
This package contains stuff used through the whole project, 
like constants, definitions and support functions.