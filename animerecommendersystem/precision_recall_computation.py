"""
Recall (also known as sensitivity) is the fraction of relevant instances that are retrieved.
Since we have no way to ask to users whether our recommendations are good or not, we compute as estimation of recall as:
    number of provided good recommendations / number of possible good recommendations
Where:
-   number of provided good recommendations is the number of animes that are recommended
    and that have been still viewed by users and have also a good rate.
-   number of possible good recommendations is the number of animes that have been viewed and have also a good rate.

Precision (also called positive predictive value) is the fraction of retrieved instances that are relevant.
As for recall, we can only compute an estimation of it, which is:
    number of provided good recommendations / total number of recommendations
Where:
-   number of provided good recommendations was explained above
-   total number of recommendations is self-explaining.
"""

from get_recommendations import get_recomm
from user_cluster_matrix import read_user_item_json

NUM_TESTS = 10
RATE_THRESHOLD = 6


def get_num_good_recomms(recommendations, user_list):
    num_good_recomms = 0
    for anime_id in recommendations:
        # Check if it is in user_list
        if anime_id in user_list:
            # If so, take its rate
            user_rate = user_list[anime_id]['rate']
            # If it is >= RATE_THRESHOLD, increase the counter
            if user_rate >= RATE_THRESHOLD:
                num_good_recomms += 1

    return num_good_recomms


def get_num_good_animes(user_list):
    num_good_animes = 0
    for anime_id in user_list:
        # Check if it is in user_list
        user_rate = user_list[anime_id]['rate']
        # If it is >= RATE_THRESHOLD, increase the counter
        if user_rate >= RATE_THRESHOLD:
            num_good_animes += 1

    return num_good_animes


if __name__ == '__main__':
    print "### RECALL AND PRECISION ESTIMATION ###"
    user_item = read_user_item_json()
    usernames = user_item.keys()
    for user in usernames[0:NUM_TESTS]:
        user_list = user_item[user]
        recommendations = get_recomm(user)
        num_good_recomms = get_num_good_recomms(recommendations, user_list)
        num_good_animes = get_num_good_animes(user_list)

        if num_good_animes > 0:
            recall = num_good_recomms/(num_good_animes+0.0)
            print "Recall estimation for user " + user + " is " + str(recall) + "."
        else:
            print "Recall estimation for user " + user + " is 0/0."

        precision = num_good_recomms/(len(recommendations)+0.0)
        print "Precision estimation for user " + user + " is " + str(precision) + "."
