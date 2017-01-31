from user_cluster_matrix import read_user_item_json


def sort_list(view_list):
    """
    :param view_list: list of watched anime by a specific user
    :return: the input list, but sorted in descending order (according to user's rate)
    """
    sorted_list = list()
    buckets = dict()

    # PHASE #1: put the objects in the right bucket
    for anime in view_list:
        # Check if it is the fist anime with that rate
        anime_rate = view_list[anime]['rate']

        if anime_rate not in buckets.keys():
            buckets[anime_rate] = list()

        # In both cases, add the anime in the correct bucket
        buckets[anime_rate].append(anime)

    # PHASE #2: get back the object in the right order (descending)
    rates = sorted(buckets.keys(), reverse=True)
    for rate in rates:
        for anime in buckets[rate]:
            print anime
            sorted_list.append(anime)

    print "### Sorting complete ###"
    return sorted_list


if __name__ == '__main__':
    user_item = read_user_item_json()

    sort_list(user_item['borf12349'])
