import json


def load_json_file(filename):
    """ Read the json file that has the specified name """
    with open(filename, 'r') as fp:
        d = json.load(fp)

    if d is not None:
        return d
    return None


def sort_list(view_list):
    """
    :param view_list: list of watched anime by a specific user
    :return: the input list, but sorted in descending order (according to user's rate)
    """
    sorted_list = list()
    buckets = dict()

    # PHASE #1: put the objects in the right bucket
    for anime in view_list['list']:
        # Check if it is the fist anime with that rate
        anime_rate = view_list['list'][anime]['rate']

        if anime_rate not in buckets.keys():
            buckets[anime_rate] = list()

        # In both cases, add the anime in the correct bucket
        buckets[anime_rate].append(anime)

    # PHASE #2: get back the object in the right order (descending)
    rates = sorted(buckets.keys(), reverse=True)
    for rate in rates:
        for anime in buckets[rate]:
            sorted_list.append(anime)

    # print "### Sorting complete ###"
    return sorted_list
