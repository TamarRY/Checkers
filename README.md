# Checkers
Implementing a smart AI computer agent for the game of checkers using the Minimax approach and Alpha-Beta pruning as optimization. 
There are few types of players: random, interactive, simple: that uses a simple partition of time in each turn and a simple utility function, 
improved: that uses a more clever partition that determines more time as long as there more turns per round, 
better_h: uses a better utility function to estimate the score for the MiniMax algorithem. 
improved_better_h: combination of a better utility and a better time partition. 
We performed a comparation between the players in different time allocations, the rusults are at the EXCEL file. 
In order to play the game run "run_game" with 3 arguments: 2 types of players and number of seconds for each round. 

