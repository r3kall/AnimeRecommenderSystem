import os
import timeit

from animerecommendersystem.utils import utils_functions

from animerecommendersystem.recommender_systems import CollaborativeFilteringRS
from animerecommendersystem.utils import definitions

if __name__ == '__main__':
    num_neighbors = 5
    file_name = train_filename = os.path.join(definitions.FILE_DIR, "user-item.json")
    users_anime_lists = utils_functions.load_json_file(file_name)
    cfrs = CollaborativeFilteringRS.CollaborativeFilteringRS(users_anime_lists, num_neighbors)

    for user in users_anime_lists.keys()[0:10]:
        start = timeit.default_timer()
        recommendations = cfrs.get_recommendations(user)
        req_time = timeit.default_timer() - start
        print "------------------------------------------------------------"
        print "Recommendations for user "+user+" are:"
        print recommendations
        print "Required time = "+str(req_time)
