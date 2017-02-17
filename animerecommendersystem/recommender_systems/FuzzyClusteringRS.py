from sklearn.neighbors import NearestNeighbors

from animerecommendersystem.utils.utils_functions import sort_list
from collections import defaultdict


STD_NUM_RECOMM = 20
STD_NUM_NEIGHBORS = 7

# Codes used for specifying the way we take recommendations from neighbors
FIRST_USER_FIRST = 0
ITERATIVE = 1

# Constants for vote prediction
MAX_PREDICT_RATE = 10.
MIN_PREDICT_RATE = 1.


class FuzzyCluseringRS:

    def __init__(self, users_anime_lists, users_clusters_matrix, users_clusters_dict,
                 users_clusters_indices, num_neighbors=STD_NUM_NEIGHBORS,
                 num_recommendations=STD_NUM_RECOMM, how_to=FIRST_USER_FIRST):

        self.users_anime_lists = users_anime_lists
        self.users_clusters_matrix = users_clusters_matrix
        self.users_clusters_dict = users_clusters_dict
        self.users_clusters_indices = users_clusters_indices

        self.num_neighbors = num_neighbors
        self.num_recommendations = num_recommendations
        self.how_to = how_to
        self.recommendations_list = list()

    def get_neighbors(self, user_name):
        neigh = NearestNeighbors(n_neighbors=self.num_neighbors+1,
                                 metric='cosine', algorithm='brute', n_jobs=-1)
        neigh.fit(self.users_clusters_matrix)

        vector = self.users_clusters_dict[user_name]
        distances, indices = neigh.kneighbors(vector.reshape(1, -1),
                                              return_distance=True)

        nearest_neighbors_dict = defaultdict(float)

        for i in range(1, self.num_neighbors+1):
            user_index = indices[0][i]
            similarity = 1. - distances[0][i]
            nearest_neighbors_dict[self.users_clusters_indices[user_index]] = similarity

        return nearest_neighbors_dict

    def get_recommendations(self, user):
        """
        :param user: Name of the user we want to give suggetions to
        :return: a list of animes that could (possibly) be interesting to him/her
        """

        # Invoke kNN on the matrix to get neighbors
        neighbors_dict = self.get_neighbors(user)

        predictions_rates_dict = defaultdict(float)
        predictions_rates_num_dict = dict()
        predictions_rates_den_dict = dict()

        user_animes = self.users_anime_lists[user]
        for neighbor in neighbors_dict.keys():
            neighbor_animes = self.users_anime_lists[neighbor]
            for anime in neighbor_animes['list'].keys():
                if anime not in user_animes['list'].keys():
                    neighbor_rate = neighbor_animes['list'][anime]['rate']
                    if neighbor_rate >= 6:
                        predictions_rates_num_dict[anime] = predictions_rates_num_dict.get(anime, 0) + \
                                                            neighbors_dict[neighbor] * \
                                                            (neighbor_rate - self.users_anime_lists[neighbor][
                                                                'mean_rate'])
                        predictions_rates_den_dict[anime] = predictions_rates_den_dict.get(anime, 0) + \
                                                            neighbors_dict[neighbor]

        for anime in predictions_rates_num_dict.keys():
            if predictions_rates_den_dict[anime] == 0:
                predictions_rates_dict[anime] = self.users_anime_lists[user]['mean_rate']
            else:
                predictions_rates_dict[anime] = self.users_anime_lists[user]['mean_rate'] + \
                                                (float(predictions_rates_num_dict[anime]) / float(
                                                    predictions_rates_den_dict[anime]))

            if predictions_rates_dict[anime] < MIN_PREDICT_RATE:
                predictions_rates_dict[anime] = MIN_PREDICT_RATE
            elif predictions_rates_dict[anime] > MAX_PREDICT_RATE:
                predictions_rates_dict[anime] = MAX_PREDICT_RATE

        sorted_animes = sorted(predictions_rates_dict, key=predictions_rates_dict.get, reverse=True)
        results = list()
        for anime in sorted_animes[:self.num_recommendations]:
            results.append((anime, predictions_rates_dict[anime]))
        return results
