import numpy as np
import matplotlib.pyplot as plt
import sys ### to deal with the arguments

import Tree
import Agent

from tqdm.auto import tqdm ### just for a nice loading bar 

def generate_a_maze( N_grid, N_episodes=500, exploration_decreasing_decay=0.01, seed=1 ):
    """
    Generate a maze on a grid of size N_grid
    input : 
    - N_grid (int) : the size of the grid
    optional input : 
    - N_episodes=500 (int) : the number of iteration in the training
    - exploration_decreasing_decay=0.01  (float) : the exponention decay to balance the exploration vs. exploitation during training
    - seed=1 (int) : the rng generator seed, fixed during test, should be change to produce different maze
    """
    np.random.seed(seed)
    tree = Tree.Cell_Tree( N_grid )
    agent = Agent.Agent(tree, N_episodes=N_episodes, exploration_decreasing_decay=exploration_decreasing_decay)
    agent.train(from_random=False )
    agent.generate( from_random=False )
    print( f"Maze doable : {tree.check()}" )
    print( f"Wall indicator {tree.Wall_state.sum()*2 / tree.N_Wall *100:.1f}%" )
    tree.visu()
    
def test_if_it_work(seed=1):
    """
    Test over 50 trial of N_grid 4
    - seed=1 (int) : the rng generator seed, fixed during test, should be change to produce different maze
    """
    np.random.seed(seed)
    N_grid = 4
    N_trial = 50
    N_Wall_trials = np.zeros(N_trial)
    N_checked = np.zeros(N_trial).astype(bool)

    for i in tqdm(np.arange(N_trial)):

        tree = Tree.Cell_Tree( N_grid )
        agent = Agent.Agent(tree, N_episodes=500, exploration_decreasing_decay=0.01)
        agent.train(from_random=False, verbose=False, disable_tdqm=True)

        agent.generate( from_random=False )
        N_Wall_trials[i] = tree.Wall_state.sum()
        N_checked[i] = tree.check()
        
    N_Wall_pc = N_Wall_trials * 2 * 100 / tree.N_Wall
    fig, ax = plt.subplots()
    x = np.arange(N_trial)
    ax.plot( x, N_Wall_pc )

    x0,x1 = ax.get_xlim()
    y0,y1 = ax.get_ylim()
    ax.set_aspect( (x1-x0)/(y1-y0) )

    ax.set_xlabel( 'Trial' )
    ax.set_ylabel( f'Wall indicator [%] ' )
    print(f"test pass {N_checked.sum()}/{N_trial}")
    plt.show()

if __name__ == "__main__":
    
    N_grid = int(sys.argv[1])
    #print( N_grid )
    generate_a_maze( N_grid, N_episodes=500, exploration_decreasing_decay=0.01, seed=1 )
    plt.show()
