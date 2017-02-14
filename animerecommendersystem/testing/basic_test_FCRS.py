from animerecommendersystem.utils import utils_functions
from animerecommendersystem.recommender_systems import FuzzyClusteringRS
from animerecommendersystem.utils import definitions

import numpy as np
import os

if __name__ == '__main__':
    file_name = train_filename = os.path.join(definitions.FILE_DIR, "user-item.json")
    users_anime_lists = utils_functions.load_json_file(file_name)

    users_clusters_dict = np.load(definitions.USER_CLUSTER_DICT).item()
    users_clusters_matrix = np.load(definitions.USER_CLUSTER_MATRIX)
    users_clusters_indices = np.load(definitions.USER_CLUSTER_INDICES).item()
    fcrs = FuzzyClusteringRS.FuzzyCluseringRS(users_anime_lists, users_clusters_matrix,
                                              users_clusters_dict, users_clusters_indices)

    user = 'Lebbing'
    recommendations = fcrs.get_recommendations(user)
    print "------------------------------------------------------------"
    print "Recommendations for user "+user+" are:"
    print recommendations
