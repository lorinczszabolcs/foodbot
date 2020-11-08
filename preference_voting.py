import numpy as np
import itertools as itr
import random as rd

# Running a simulation based on the Terry-Bradley method
# Generating a set of votes #
# matrix of 0's #
# i,j dim = of candidate restaurants #


# in this case number of candidate restaurants must at least equal nC2 number of team members #

# This function takes the restaurant list of ids and team numbers to generate a sample allocation scheme
def alloc_team_sample(restlist, teamnum):
    # creating a list of all possible combinations and changing restaurant names into indexes
    restnum = range(len(restlist))
    pw_list  = list(itr.combinations(restnum, 2))
    comparison_list = []

    for i in range(0, len(pw_list)):
        comparison_list.append(pw_list[i])

    # Sample pairs to allocate in a random manner
    ipairs = rd.sample(comparison_list, len(comparison_list))
    # creating an allocation list for which pairs each person gets
    allocation_list = [[] for i in range(teamnum)]
    # allocate to team members in an iterative format
    for i in range(0, len(comparison_list)):
        allocation_list[(i % teamnum)].append(ipairs[i])

    return allocation_list


# create matrix based on above winners and losers arrays
# the output is input for the btm method
def voteaggregate(winners, losers, restaurant_name):
    votesmat = np.array(
        [[0 for i in range(len(restaurant_name))] for j in range(len(restaurant_name))]
    )
    # populate matrix
    for i in range(len(winners)):
        votesmat[winners[i]][losers[i]] = votesmat[winners[i]][losers[i]] + 1
    # returns the matrix for input into the BT algorithm
    return votesmat


# Bradley-Terry method - it doesn't have a sparse data adjustment method
def btm(
    votes,
    restaurants,
    max_iter=100,
    tol=10 ** -8,
):

    n = len(restaurants)
    # votes between restaurants
    # creates a matrix of total votes
    N = votes + votes.transpose()
    # wins for each restaurants
    W = np.sum(votes, axis=1)
    # initialisation
    w_0 = np.repeat(1 / n, n)
    w_old = np.repeat(n, n)
    iter = 0

    while iter <= max_iter and np.sum((w_old - w_0) ** 2) > tol:
        iter = iter + 1
        w_old = w_0

        for i in range(n):
            tmp = 0

            for j in range(n):
                if i != j:
                    tmp = tmp + N[i, j] / (w_0[i] + w_0[j])

            w_0[i] = W[i] * tmp ** (-1)

        w_0 = w_0 / np.sum(w_0)

    # can replace the first list with the list of restaurant names in the future
    preference = [restaurants, list(w_0)]
    return preference


# Converting to an array of winners and losers with 1 if they are a winner
### Creating a matrix with the grouped output ###


### example call code to the sample
# allocating a sample
# 1st parameter - list of restaurants, 2nd parameter team members
# allocations = alloc_team_sample(["BK","MD","KFC","HES"], 7)
# allocations

### The following example calls can be used for the voteaggreate and btm
# person order does not matter for this
# example 1 - 4 restaurants
# restaurant_name = ["BK","MD","KFC","HES"]
# winners = [0, 2, 1, 1, 1, 0]
# losers =  [2, 3, 0, 2, 3, 3]
# restaurants = 4
# v1 = voteaggregate(winners,losers,restaurant_name)
# prefs = btm(v1,restaurant_name)
# prefs

# example 2 - 5 restaurants
# restaurant_name = ["BK","MD","KFC","HES","SUB"]
# winners = [2,2,4,1,1,4,0,1,2,4]
# losers = [3,0,0,4,3,3,3,0,1,2]
# restaurants = 5
# v2 = voteaggregate(winners,losers,restaurant_name)
# prefs = btm(v2,restaurant_name)
# prefs
