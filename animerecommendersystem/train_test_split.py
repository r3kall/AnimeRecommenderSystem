"""
Build training and testing files splitting animes.
Starting from a list that contains all ids of animes we have, i divide them in 5 logical groups, where
4 of them are training set and 1 is testing set.
Once established the logical sets, for each couple train-test:
    - build a new user-item-json containing only training items
    - build a new user-item-json containig only testing items
    - build user-cluster-matrix and the other files of clustering from just user-item-json-training
"""
import os
import json
import definitions
from user_cluster_matrix import read_user_item_json

# Constants
ANIME_ID_FIELD = 'anime_id'
RATE_FIELD = 'rate'
CURR_STATE_FIELD = 'curr_state'
LIST_FIELD = 'list'
MEAN_RATE = 'mean_rate'

TESTING_SIZE = 0.2


def build_id_list():
    """
    :return: List of animes ids we have, from filenames
    """
    res = list()
    html_anime_list = os.listdir(definitions.HTML_DIR)
    for anime_file in html_anime_list:
        res.append(anime_file[:len(anime_file)-5])
    return res


def split(list_animes, permutation):
    """
    :param list_animes: total anime ids
    :param permutation: Number of selected permutation (e.g first partition is test set, second partition ...etc.
    :return: Training and testing lists of anime ids
    """
    train_list = list()
    test_list = list()

    block_size = int(len(list_animes) * TESTING_SIZE)
    starting_point = block_size * permutation
    ending_point = starting_point + block_size

    # Test set
    for anime in list_animes[starting_point: ending_point]:
        test_list.append(anime)

    # Train set
    for anime2 in list_animes[0: starting_point]:
        train_list.append(anime2)
    for anime2 in list_animes[ending_point:]:
        train_list.append(anime2)

    return train_list, test_list


def add_anime(users_json, username, anime_id, rate, curr_state):
    """
    :param users_json: json we are modifying.
    :param username:user we are modifying.
    :param anime_id: id of the anime to be added to user's list.
    :param rate: from 0 to 10, represents the grade given by the user to
                 that anime. Zero means no rate.
    :param curr_state: completed, current, dropped and so on.
    :return: updates the sparse matrix of users, and returns nothing.
    """
    anime_record = {
            RATE_FIELD: rate,
            CURR_STATE_FIELD: curr_state,
    }

    if users_json.get(username) is None:
        users_json[username] = {}
    if users_json[username].get(LIST_FIELD) is None:
        users_json[username][LIST_FIELD] = {}

    users_json[username][LIST_FIELD][anime_id] = anime_record


if __name__ == '__main__':
    list_animes = build_id_list()

    # read complete json
    user_item = read_user_item_json()

    # for each partition
    for i in range(0, 5):
        print i
        train, test = split(list_animes, i)
        # initialize two jsons we need
        user_item_json_train_i = {}
        user_item_json_test_i = {}

        # for each user
        for user in user_item.keys():
            # initialize mean rates, will be computed at the end for each user in each json
            mean_rate_train = 0
            mean_rate_test = 0

            # update anime lists in jsons
            for anime in user_item[user]:
                if anime in train:
                    add_anime(user_item_json_train_i, user, anime, user_item[user][anime][RATE_FIELD],
                              user_item[user][anime][CURR_STATE_FIELD])
                    mean_rate_train += user_item[user][anime][RATE_FIELD]
                elif anime in test:
                    add_anime(user_item_json_test_i, user, anime, user_item[user][anime][RATE_FIELD],
                              user_item[user][anime][CURR_STATE_FIELD])
                    mean_rate_test += user_item[user][anime][RATE_FIELD]
            # update mean rates
            if mean_rate_train != 0:
                user_item_json_train_i[user][MEAN_RATE] = mean_rate_train/len(user_item_json_train_i[user][LIST_FIELD].keys())
            else:
                user_item_json_train_i[user][MEAN_RATE] = 0

            if mean_rate_test != 0:
                user_item_json_test_i[user][MEAN_RATE] = mean_rate_test / len(
                    user_item_json_test_i[user][LIST_FIELD].keys())
            else:
                user_item_json_test_i[user][MEAN_RATE] = 0

        # save on file
        filename_train = "user_item_train_"+str(i)+".json"
        file_train = os.path.join(definitions.FILE_DIR, filename_train)

        filename_test = "user_item_test_"+str(i)+".json"
        file_test = os.path.join(definitions.FILE_DIR, filename_test)

        with open(file_train, 'w') as fp:
            j = json.dump(user_item_json_train_i, fp)
        with open(file_test, 'w') as fp2:
            j = json.dump(user_item_json_test_i, fp2)
