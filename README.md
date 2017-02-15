# Anime Recommender System
**Sapienza - Università di Roma** <br/>
*Master of Science in Engineering in Computer Science* <br/>
*Data Mining, a.y. 2016-17* <br/>

**Introduction** <br/>
This project is a recommendation system for the myanimelist.net platform,
a web site where users can rate animes and build profiles where they write 
animes they have seen, animes they want to see in the future, 
animes they dropped and so on. 
We developed two systems:
the first uses a Collaborative Filtering technique, the second is an hybrid 
of Collaborative Filtering and Content Based techniques that perform dimensional
 reduction through the Fuzzy Clustering algorithm (Fuzzy C-Means).
 We analyse the performance of both in terms of accuracy and time.

**Datasets** <br/>
*Anime* <br/>
We downloaded more than 12000 animes, that consist of the whole dataset 
of the web site.
For each of them, we are interested in their type 
(TV Series, Movies, Specials etc.), their genre (School, Action etc.) 
and their demography (under-13 etc.), with a total of 57 binary features: 
a 0-1 feature indicates that an anime has or not that feature, 
that is a value of the elds we are interested in.
So we kept a json representing the item-feature matrix.

*Users* <br/>
We downloaded 9868 users. For each user, we picked his anime list, 
that contains various sections (Watching, Completed, On Hold, Dropped, Planned),
 each containing animes with either an integer rate from 1 to 10, 
 or 0 if the user did not vote it.
So we kept a json representing the user-item matrix.

**Collaborative Filtering** <br/>
The main idea of a collaborative filtering technique, 
in particular a user-based one, is  making automatic predictions (filtering)
about the interests of a user by collecting preferences or taste information
 from many users (collaborating), that are his nearest neighbors,
  meaning those users that watched similar animes and gave similar rates
   to them. From these predictions we make recommendations. <br/>
   
So a first naive approach is based on applying k-nearest neighbor 
on user-item matrix, and then using the ratings from those neighbors 
to calculate predictions for the active user, with the following formula: <br/> 

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/d2a94dc0a962bd32eda90d13806cc446f6dcc46c" align="middle"/> <br/><br/>
<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/ca896baefcaade46d3d20adb0ac63287ff9353e7"  align="middle"/> <br/><br/>

The recommendations are the animes with the highest predictions. <br/>
However, this approach becomes really slow, especially if the system 
has a high number of users. Therefore, we decided to add to the system 
a neighbors-search that does not compute the exact nearest neighbors, 
but to get k users that are “sufficiently close” to our target, 
meaning those the first k users whose distance is below a given 
threshold. To decide the threshold value, we performed tests on about 
1000 users and we obtained that the average distance of the nearest 
neighbors was around 0.6, and then we defined the threshold as 
0.6*1.1 = 0.66, where 1.1 is a relaxation factor.

**Fuzzy Clustering** <br/>
As the numbers of users and items grow, traditional CF algorithms 
will suffer serious scalability problems. So, one of the biggest 
problems with recommendation systems based on CF is the Curse of
 Dimensionality: these systems are highly sensitive to the increasing
  number of users in the system. Classical ways to alleviate this issue
   is to perform Dimensional Reduction like, for example, 
   Singular Value Decomposition (SVD).
We use a technique that, at the same time, reduces dimensionality 
and combines Content based information with the CF system: <br/>

* Given the items matrix (MxF), where M is the number of items and 
F is the number of binary feature, and where each item has a binary 
array representing his features (type, genre, demography, ...),
 we perform Fuzzy Clustering, using the C-Means algorithm,
  on this binary matrix, in order to obtain a soft-assignment
   with probability membership of an item to a cluster,
    obtaining an item-cluster matrix (MxC), with C number of clusters.
* We combine the item-cluster matrix with the user-item matrix 
(or Utility matrix) with dimension (NxM), N number of users, 
obtaining through weighted mean the user-clusters matrix of dimension 
(NxC), where each element represent the probability of a user to belong 
to a cluster.
* We perform, like in the CF system, K-Nearest Neighbors on the 
user-cluster matrix, and get prediction using the same approach.

**Evaluation Metrics and Tuning Step** <br/>
To evaluate the quality of our systems, we used:
* the root-mean-square error (RMSE) measure, defined as: <br/>
<img src="http://statweb.stanford.edu/~susan/courses/s60/split/img29.png" align="middle"/> <br/><br/>
where n is the number of recommendations, y^<sub>t</sub> is the predicted rate, and y<sub>t</sub> is the real rate the user gave to the anime t.

* the mean absolute error (MAE) measure, defined as: <br/>
<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/a26cd07ce591210dc494cec532c4dacfdf9153b9" align="middle"/> <br/><br/>
where f<sub>i</sub> is the predicted rate for anime i, and y<sub>i</sub> is the real rate the user gave to it.

These two measures were used during the training phase to decide 
with parameters within the system perform better. 
For the recommender system based on collaborative filtering technique, 
we performed training on the number of neighbors used to compute
 recommendations, while for the one based on fuzzy clustering 
 we tuned the number of clusters too.
 
**Graph and Tables** <br/>
TODO

**Conclusions** <br/>
To measure the similarity between users we used the cosine similarity between their rating vectors. In both systems it proved to be better than Pearson similarity.

From the graph attached above, we can see that, even if he recommender 
system based on fuzzy clustering is a bit worse than the collaborative 
filtering one, it is way faster (about SIX TIMES -ADD REAL VALUE), 
and therefore it can be considered better than the other one.


**References** <br/>
TODO


