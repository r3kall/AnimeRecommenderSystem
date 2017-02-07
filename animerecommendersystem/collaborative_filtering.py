"""
This files offers (i.e., will offer) a recommendation system based on collaborative filtering technique.
1)  Let U be the user we want to give recommendations to, for each user U2 != U we need to compute distance(U, U2) (*)
    and get the top K neighbors. These neighbors should have watched a lot of animes also watched by U,
    giving to them similar rates.
2)  Once we have these K neighbors, we compute an aggregate rate to the animes they watched
    by using the rates given by them (excluding the ones already watched by U, obviously).
    In other words, we try to return as recommendations the animes watched by most of the neighbors
    and with an high rate by (almost) all of them.

(*)HOW DO WE COMPUTE THE DISTANCE BETWEEN U AND U2?
Idea: something similar to cosine similarity
In particolar, for each anime watched by both users, we should compute the product of rates
=> PROBLEM: what if an user didn't rate this anime?
    => We need to estimate this rate.
    => PROBLEM: how?
        => First idea:  use the average of all rates he gave to other animes he watched.
        => Second idea: use the average of all rates he gave to other anime he watched IN THE SAME STATE.
        => Third idea:  use a predefined rate according to the anime state (e.g., we give '4' to it if it is Dropped).
"""

if __name__ == '__main__':
    print "TODO"
