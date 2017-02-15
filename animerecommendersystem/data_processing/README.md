# Data Processing
**Sapienza - Università di Roma** <br/>
*Master of Science in Engineering in Computer Science* <br/>
*Data Mining, a.y. 2016-17* <br/>

This package is composed of files that build the data structures
we need.

## item_cluster_matrix.py
This file contains two main functions:
* build_item_feature_matrix: as the name suggests, it returns a
item_feature matrix numpy matrix from the item_feature dictionary that
we built when downloading the animes;
* item_cluster_matrix: it performs fuzzy c means algorithm and returns
 the item-cluster matrix, from the item-feature matrix.

## train_test_split.py
This file splits the animes in train and test set, and
then builds 5 train and 5 test user-item json files, by looking at
the list of animes of each user. These json files are needed when
performing the evaluation of the system using k-fold, where at
each iteration we work with a reduced matrix.

## user_scraping.py
This file has a main function that is scrape_page, that takes as
input a file containing a user's anime list and extracts from it
all relevant fields, that are the anime id, its rate and its status
(COMPLETED, WATCHING, ON HOLD, DROPPED, PLANNED), and builds the
user-item json file, that for each user contains a list with
a record for each anime containing those fields, plus a field with
the average rate of the user.

## user_cluster_matrix.py
This file builds the user-cluster matrix, that contains for each user
the probability of belonging to each cluster. This matrix is
computed from the user-item json and the item-cluster matrix.
For each user, this probability is computed in this way: for each
anime in the user list, such that its ranking is valid
(the anime is not PLANNED) sum to the result the product of the
 probability of this anime to belong to that cluster, and a ranking
 that is equal to the mean rate of the user, if the anime is not
 dropped, else the maximum between 2 and the mean rate divided by 2.