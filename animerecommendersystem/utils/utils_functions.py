import json


def load_json_file(filename):
    """ Read the json file that has the specified name """
    with open(filename, 'r') as fp:
        d = json.load(fp)

    if d is not None:
        return d
    return None
