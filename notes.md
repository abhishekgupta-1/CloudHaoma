### Description of variables
#### On Leader Node
1. nextIndex[followerId] - Index of the log on the followerId node for which leader will be sending the data
2. matchIndex[followerId] - Logs on the followerId node and leader completely match till matchIndex[followerId]. Note matchIndex[followerId] = nextIndex[followerId-1]
3. 


### Pointers
1. For starting election timeout, use electionTimeCall = False, shift = True

2. 