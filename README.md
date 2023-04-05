# MAZE_generator
 a Maze generator with Q-Learning

# How to use

# Algorythm
This section will describ the algorythm choises made. 

## Specifications 
The specifications impose the use the Q-learning algorythm to generate a doable maze.

But the specifications do not defined what is a 'do-able Maze' : 
- is a grid with no wall a 'do-able Maze'?
- is a grid with only one wall a 'do-able Maze'?

I assume that a 'do-able **nice** Maze' is : 
- any doable grid
- a grid with a minimum of walls, but not too much (one way maze...). So maximize the number of walls up to half the total number of wall possible seems a good esthetical compromise.

## Maze management

### The tree

## Q-learning management

### Actions

### States

### Rewards


# Architecture
 The code is based on 2 main class : 
 - One to manage the maze's grid and walls : Tree.py
 - One to manage the Q-learning : Agent.py

## Tree.py
