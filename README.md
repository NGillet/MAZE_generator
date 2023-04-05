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

Three main fonctions associated to the maze are needed by the generator : 
- Define the START, EXIT and CHEST cells
- Build Walls
- Check if the maze is doable

To construct those functions, I describe the grid of the maze as a tree of linked cells

### The tree

The grid is composed of cells, cells have neighbors, the transition between cells is a wall, the wall can be build (up, true...) or not (down, false...).

![schéma](https://user-images.githubusercontent.com/12394419/230098839-f8318f27-3fee-49e6-851c-7aa4c66a78e3.png)
*Fig 1 : on the left : a 4x4 grid with cells and walls IDs. On the right : the tree associate to the grid. NOTE : the shape of the tree change with the START cell.*

The tree is compose of layers, each layer is a list of cells. The tree is build recursivelly from the first layer, which contain only the starting cell. Then each layer is build from the neighbors cells of the previous layer, **for cells 
that are not already in the tree** (to avoid infinit loop). Each cell store the next cells and its previous cells. 

The tree structure permits to 'build wall' by removing a cell in the 'next' and 'previous' list. By going from cell to 'next' and 'previous' it is possible to check if the EXIT and CHEST cells are connected to the start cell. 



## Q-learning management

### Actions

### States

### Rewards


# Architecture
 The code is based on 2 main class : 
 - One to manage the maze's grid and walls : Tree.py
 
 - One to manage the Q-learning : Agent.py

## Tree.py
