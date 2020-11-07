import numpy as np
import itertools as itr
import random as rd

# This simulates purely random choice behaviour for our model #
def simulate_vote(allocation_list) :

    winners=[]
    losers=[]
    # Iterate through the allocation list
    for i in range(len(allocation_list)) :
        for j in range(len(allocation_list[i])) :
            # make a random vote for the pairchoice
            x = rd.random()
            if (x > 0.5) :
                # votes for choice 0 #
                winners.append(allocation_list[i][j][0])
                losers.append(allocation_list[i][j][1])
                # votes for choice 1 #
            else :
                winners.append(allocation_list[i][j][1])
                losers.append(allocation_list[i][j][0])

    return(winners,losers)

# Example
#allocations = alloc_team_sample(["BK","MD","KFC","HES","SUB"], 7)
#sim_vote = simulate_vote(allocations)
#print(sim_vote)
