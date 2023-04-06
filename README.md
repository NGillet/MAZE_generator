# MAZE_generator
 a Maze generator with Q-Learning

# Usage

Python3, numpy, matplotlib and tqdm for 'nice' loading bar (and have a quick estimate of the waiting time). If it does not work you can remove it manually ( in maze_generator.py line 30 and in Agent.py line 37 )

In the next examples sections, the seed of the rng is fixed to 1, so the results should be identical.
## In command line 

to create a maze of size N_Grid, give the size of the grid in argument :

```console
> python maze_generator.py 6
100%|██████████████████████████████████████████████████████████████████████████████████| 500/500 [00:10<00:00, 46.97it/s]
Maze doable : True
Wall indicator 96.7%
```
![plot1](https://user-images.githubusercontent.com/12394419/230307262-1adc7b06-b81f-40f0-9254-e11dd10f0e9a.png)

*a matplotlib popup plot should appear*

- The loading bar giving the advancement of the training
- `Maze doable : True` : tell if the maze is doable
- `Wall indicator 96.7%` : a quick estimate if the maze is 'nice' (100% is half of the walls build)

## As a module 

```console
>>> import maze_generator as mg
>>> mg.generate_a_maze( 6, N_episodes=500, exploration_decreasing_decay=0.01, seed=1 )
```
It should produce the same result as the previous example. Note that you can change the seed number to produce different maze.

## large maze : 15 and 20

```console
> python maze_generator.py 15
100%|██████████████████████████████████████████████████████████████████████████████████| 500/500 [05:24<00:00,  1.54it/s]
Maze doable : True
Wall indicator 114.3%
```
![plot3](https://user-images.githubusercontent.com/12394419/230314484-f4cc3124-5c36-40bc-83ed-1444edb41108.png)

it takes ~5min


```console
> python maze_generator.py 20
100%|██████████████████████████████████████████████████████████████████████████████████| 500/500 [34:43<00:00,  4.17s/it]
Maze doable : True
Wall indicator 110.3%
```
![plot4](https://user-images.githubusercontent.com/12394419/230324132-22f05b03-69de-459e-844b-4901ec89e77c.png)

it takes ~30min


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

Note : I also assume a square box, which is not in the specification. It does not change fundamentally the algorythm used here. The changment to a rectangular grid is not obvious, because the square grid is hard coded in several formula (in the position of cells and walls especially), but it is doable. 

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

This section is not maint to explain the Q-learning algorythm, but to explain the choise made. 
The three main parameters to setup are the actions possible of the agent, the states of the grid and rewards.

### Actions
The actions are 'build one of wall' and 'stop building' (the maze is done). Therefore the number of action is equal to number of wall plus one.

### States
The states are the current number of walls on the grid. Therefore the number of wall is also equal to number of wall plus one (from 0 wall to all wall build).

### Rewards
I defined three rewards : 
1. Reward for finishing a doable maze : it encourage the agent to stop building wall while the maze is doable
2. Reward for building walls : it encourage the agent to build walls
3. Penality for building a wall that brake the maze

The rewards (1) and (2) are adversarial, by adjusting the value of the reward we could build **nice doable maze**. 

### Hyper-parameters
There are other parameters that have to defined : 
- learning rate : 
- discount : 
- exploration/exploitation exponential decay : 
- number of iteration :

# Architecture
 The code is based on 2 main class : 
 - One to manage the maze's grid and walls : Tree.py
 - One to manage the Q-learning : Agent.py

## Tree.py
Contain 2 class : 
- `class Cell:` represent a cell of the grid, it contain its position (1D and 2D) and the list of neighbors, next and previous cells. Note that the next and previous list are only defined and usefull in the tree structure.
- `class Cell_Tree:` represent the grid : 
    - it create the special cells : START, EXIT and CHEST
    - it generate the tree recursivelly
    - it has function to build or brake walls
    - it has function to check if the maze is doable

## Agent.py
Contain one class :
- `class Agent(tree):` it take a tree in input, and permit to manage the agent for the Q-learning and generate a maze. It has two main functions :
    - `def train():` train the agent to build a **nice doable maze**
    - `def generate():` generate the maze from the Q-value matrix (after training)
    
    
# Discussion

## Additional function

A function to generate 50 maze and check if they are **nice doable maze** :

```console
>>> import maze_generator as mg
>>> mg.test_if_it_work()
100%|██████████████████████████████████████████████████████████████████████████████████| 50/50 [01:14<00:00,  1.49s/it]
test pass 46/50
```

On 50 trail, 46 maze were doable, 4 failed to be properlly generated.

![plot2](https://user-images.githubusercontent.com/12394419/230311239-89a9dac9-1ff7-4b3f-be8e-298ae2ade1ee.png)

The figure above give the 'quality' of the 50 generated maze. We can note 4 mazes that generate only 1 wall. Otherwise the other 46 have a good quality, between 80%-100%.

Conclusion : Out of 50 trials, 4 failed, 4 were poor quality : so 82% efficiency

## Learning time vs convergence
during the developement I tryed to optimize some hyper parameters to fasten the leanrning. In the end it is a compromise between optimize the learning time and publish the code.

- `learning rate = 0.1` which might be a bit weak.
- `discount = 1` which might be too much... to compensate the weak learning rate
- the couple `N_episodes=500`, `exploration_decreasing_decay=0.01` seems to alow the convergence in most cases tested

## Estimation of the difficulty of the generated maze

The main estimator of the difficulty of a maze could be : the number of move needed to reach the EXIT (or the CHEST then the EXIT).
The estimator is not perfect, you can imagine a long hallway... but in **nice doable maze** it is a good estimator

I see two ways to compute the number of needed move : 
- by using the tree to explore 'all' the ways to the end : this require a 'small' adaptation of the checking function
- by using Q-learning in a 'classical' way, to explore and solve the maze, then count the number of move in the final way found 
