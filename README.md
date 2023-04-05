# MAZE_generator
 a Maze generator with Q-Learning

# How to use

# Algorythm
This section will describ the algorythm choises made. 
## Specifications 
The specifications impose the use of Q-learning algorythm to generate a doable maze.

But the specifications do not defined what is a 'do-able Maze' : 
- is a grid with no wall a 'do-able Maze'?
- is a grid with only one wall a 'do-able Maze'?

Here are the assumptions I fixed about a 'do-able **nice** Maze' : 
- any doable grid is a correct answer
- **nice** Maze : an interesting maze should have a minimum of walls, but not too much (one way maze...). So maximize the number of walls up to half the total number of wall possible seems a good esthetical compromise.



# Architecture
 The code is based on 2 main class : 
 - One to manage the maze's grid and walls : Tree.py
 - One to manage the Q-learning : Agent.py

## Tree.py
