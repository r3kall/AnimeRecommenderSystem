"""
This files offers a recommendation system based on collaborative filtering technique.
1)  Let U be the user we want to give recommendations to, for each user U2 != U we need to compute distance(U, U2) (*)
    and get the top K neighbors. These neighbors should have watched a lot of animes also watched by U,
    giving to them similar rates.
2)  Once we have these K neighbors, we compute an aggregate rate to the animes they watched
    by using the rates given by them (excluding the ones already watched by U, obviously).
    In other words, we try to return as recommendations the animes watched by most of the neighbors
    and with an high rate by (almost) all of them.

(*)HOW DO WE COMPUTE THE DISTANCE BETWEEN U AND U2?
Idea: cosine similarity
In particolar, for each anime watched by both users, we should compute the product of rates.
"""
from collections import defaultdict
import math

STD_NUM_RECOMM = 10
AVG_NEAREST_DISTANCE = 0.50
RELAX_RATIO = 1.1


class CollaborativeFilteringRS:

    def __init__(self, users_anime_lists, num_neighbors, num_recommendations=STD_NUM_RECOMM, approx=True):
        self.users_anime_lists = users_anime_lists
        self.num_neighbors = num_neighbors
        self.num_recommendations = num_recommendations
        self.approx = approx

    def compute_distance(self, username1, username2):
        # Take the list of animes for each user
        user1_animes = self.users_anime_lists[username1]
        user2_animes = self.users_anime_lists[username2]

        distance_numerator = 0
        square_sum_1 = 0
        square_sum_2 = 0

        # Create a set that contains animes watched by at least one of the user.
        total_set_animes = set(user1_animes['list'].keys())
        total_set_animes |= set(user2_animes['list'].keys())
        for anime in total_set_animes:
            watched1 = False
            watched2 = False
            user1_rate = 0
            user2_rate = 0

            if anime in user1_animes['list'].keys():
                watched1 = True
                user1_rate = user1_animes['list'][anime]['rate']
                if user1_rate == 0:
                    user1_rate = estimate_rate(user1_animes, anime)

                square_sum_1 += user1_rate * user1_rate

            if anime in user2_animes['list'].keys():
                watched2 = True

                user2_rate = user2_animes['list'][anime]['rate']
                if user2_rate == 0:
                    user2_rate = estimate_rate(user2_animes, anime)

                square_sum_2 += user2_rate * user2_rate

            # If both users' lists contain this anime, then we need to increase the similarity
            if watched1 and watched2:
                distance_numerator += user1_rate * user2_rate

        # At the end, use the values collected so far to compute the distance between users.
        distance_denominator = math.sqrt(square_sum_1) * math.sqrt(square_sum_2)
        similarity = distance_numerator / distance_denominator
        distance = 1 - similarity
        return distance

    def get_neighbors(self, user):
        if self.approx is True:
            return self.get_approx_neighbors(user)
        else:
            return self.get_exact_neighbors(user)

    def get_approx_neighbors(self, user):
        """
            Basic idea: compute distance between 'username''s list and all other users, and pick the nearest ones.
            => PROBLEM: TOO SLOW.
            => SOLUTION: no need to pick the nearest one, but some near users will be still ok.
        """
        neighbors = defaultdict(float)
        how_many_good = 0
        for user2 in self.users_anime_lists.keys():
            if user2 == user or self.users_anime_lists[user2].get('list') is None:
                continue

            distance = compute_distance(user, user2, self.users_anime_lists)
            neighbors[user2] = distance

            # If this user is close enough to our target, then we take him as a neighbor
            if distance <= AVG_NEAREST_DISTANCE * RELAX_RATIO:
                how_many_good += 1

            if how_many_good == self.num_neighbors:
                break
        # Sort neighbors according to distance, and return them
        sorted_neighbors = sorted(neighbors, key=neighbors.get, reverse=False)

        # return a dict, so we have also the similarity as info
        res = dict()
        for neighbor in sorted_neighbors[0:self.num_neighbors]:
            # similarity
            res[neighbor] = 1 - neighbors[neighbor]
        return res

    def get_exact_neighbors(self, user):
        distances_dict = defaultdict(float)
        for user2 in self.users_anime_lists.keys():
            if user2 == user or self.users_anime_lists[user2].get('list') is None:
                continue

            distance = self.compute_distance(user, user2)
            distances_dict[user2] = distance
        # Once we have all distances, sort the dict by value and return a list containing
        # the usernames of the nearest ones.
        sorted_neighbors = sorted(distances_dict, key=distances_dict.get, reverse=False)
        return sorted_neighbors[0:self.num_neighbors]

    def get_recommendations(self, user):
        print "TODO"

        neighbors_dict = self.get_neighbors(user)

        # TODO get anime
