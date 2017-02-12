from sklearn.neighbors import NearestNeighbors

from animerecommendersystem.utils.utils_functions import sort_list
from animerecommendersystem.data_processing.user_cluster_matrix import read_user_item_json
from animerecommendersystem.utils import definitions


STD_NUM_RECOMM = 10
STD_NUM_NEIGHBORS = 5

# Codes used for specifying the way we take recommendations from neighbors
FIRST_USER_FIRST = 0
ITERATIVE = 1


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
        neigh = NearestNeighbors(n_neighbors=self.num_neighbors)
        neigh.fit(self.users_clusters_matrix)

        vector = self.users_clusters_dict[user_name]
        distances, indices = neigh.kneighbors(vector.reshape(1, -1))

        nearest_neighbors_list = list()
        for i in indices[0][1:]:
            nearest_neighbors_list.append(self.users_clusters_indices[i])

        return nearest_neighbors_list

    @staticmethod
    def get_num_recomm(i):
        """
        :param i: Position of the neighbor (e.g., zero = the closest one to our target user)
        :return: number of anime we want to take from this neighbor as a recommendation.
        """
        if i == 0:
            return 4
        elif i == 1:
            return 3
        elif i == 2:
            return 2
        else:
            return 1

    def get_recomm_from_user(self, k, neighbor, user):
        """
        :param k: number of recommendations we want to take from this user
        :param neighbor: name of the user we want to take stuff from
        :param user: name of the user we want to suggest stuff to
        :return: Nothing, but modifies the self.recommendations_list adding (hopefully) other recommendations.
        """
        neighbor_list = self.users_anime_lists[neighbor]
        user_list = self.users_anime_lists[user]

        # Sort it in descending order
        neighbor_sorted_list = sort_list(neighbor_list)

        for possible_recommendation in neighbor_sorted_list:
            # Check whether it is contained into anime_list
            if (possible_recommendation not in self.recommendations_list) and \
                    (possible_recommendation not in user_list):
                k -= 1
                self.recommendations_list.append(possible_recommendation)

            # If we already took the requested recommendations from this user, we can just stop cycling.
            if k == 0:
                break

        # We arrive here only if the neighbor has not enough anime to suggest.
        return k

    def iterative_get_recom(self, neighbors_list, user):
        """
        Support function for get_recom(), called if how_to is equal to ITERATIVE
        :param neighbors_list: list of users 'close' to our client's target.
        :param user: name of the user we want to recommend stuff to
        :return: Nothing, but at the end self.recommendations_list will be a list of recommendations
                 computed by taking some animes from each user (hopefully),
                 and iterating on them if the stuff we took is insufficient.
        """
        current_recom_list = list()
        previous_recom_list = list()

        k = self.num_recommendations
        while k > 0:
            previous_recom_list = current_recom_list
            i = 0
            for neigh in neighbors_list:
                # Example: if we need only 3 more animes (i.e., k=3), but by default we would take 4,
                # we need to reduce how_many.
                how_many = min(k, self.get_num_recomm(i))
                remainder = self.get_recomm_from_user(how_many, neigh, user)
                i += 1
                k -= how_many - remainder
                if k == 0:
                    break

            current_recom_list = self.recommendations_list
            # If the last iteration did not add anything, there's no reason to keep iterating.
            if current_recom_list == previous_recom_list:
                break

    def get_recommendations(self, user):
        """
        :param user: Name of the user we want to give suggetions to
        :return: a list of animes that could (possibly) be interesting to him/her
        """
        """
        # read from files computed in user_cluster_matrix.py
        user_cluster_dict = np.load(definitions.USER_CLUSTER_DICT).item()
        user_cluster_matrix = np.load(definitions.USER_CLUSTER_MATRIX)
        user_cluster_indices = np.load(definitions.USER_CLUSTER_INDICES).item()
        """

        # Invoke kNN on the matrix to get neighbors
        neighbors_list = self.get_neighbors(user)

        user_anime_list = self.users_anime_lists[user].keys()

        # For each neighbor, take some anime
        self.recommendations_list = list()

        if self.how_to == FIRST_USER_FIRST:
            for neigh in neighbors_list:
                k = self.get_recomm_from_user(self.num_recommendations, neigh, user)
                if k == 0:
                    break

        elif self.how_to == ITERATIVE:
            self.iterative_get_recom(neighbors_list, user)

        # Return them
        return self.recommendations_list
