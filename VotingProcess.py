import numpy as np

from AITOinterface import names
from Votesample import alloc_team_sample, voteaggregate, btm
from RandomChoice import simulate_vote

# We use information collected from the Bot to determine for how many team members #
teamnum = 5
# This information then gets sent to the AITO DB to find the restaurants that best fit the criteria

# We use a list of restaurants as given by a call to the AITO library #
# currently stored as "names"
# We restrict the number of voting choices by only considering a subset - at the moment we set it to 5 #
# it could even be a subsample if we want further randomness #
votenames = names[0:10]

# Now the voting process starts here #

# Allocating pairwise comparisons to people
voting_allocation = alloc_team_sample(votenames,teamnum)

# Send allocation to the simulated voting function
sim_vote = simulate_vote(voting_allocation)
# Create a winner/loser table
vote_result = voteaggregate(sim_vote[0],sim_vote[1],votenames)

# Now send it to find the highest pref using the Bradley Terry Method #
preflist = btm(vote_result,votenames)
highestpref = preflist[0][preflist[1].index(np.max(preflist[1]))]

# Send the highest preferred restaurant to people! #
print("Your team chose ... ", highestpref)