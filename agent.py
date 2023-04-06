import numpy as np
import matplotlib.pyplot as plt

from tqdm.auto import tqdm ### just for a nice loading bar 

class Agent():
    def __init__(self, tree, N_episodes=500, exploration_decreasing_decay=0.01):  ### tree en input ?
        
        self.tree = tree ### the grid structure
    
        ### init Q-table
        self.N_state = self.tree.N_Wall+1 
        self.N_action = self.tree.N_Wall+1
        self.Q_table = np.zeros(( self.N_state, self.N_action ))
        
        ### hyper params
        self.N_max_action = self.N_action*2
        ### Exploration
        self.exploration_proba = 1 ### init of the proba
        self.exploration_decreasing_decay = exploration_decreasing_decay  ### decreasing decay for exponential decreasing
        self.min_exploration_proba = 0.01 ### Minimum of exploration proba

        if 1: self.N_episodes = N_episodes
        else : self.N_episodes = np.ceil( np.log( self.min_exploration_proba ) / -self.exploration_decreasing_decay ).astype(int)
        #print( 'N_episodes ',N_episodes )

        self.discount = 1. ### Discounted factor
        self.lr = 0.1 ### learning rate

        ### Metrics
        self.total_rewards_episode = np.zeros( self.N_episodes )
        self.total_QV_episode = np.zeros( self.N_episodes )
                  
    def train(self, from_random=False, verbose=True, disable_tdqm=False):
        ### we iterate over episodes
        #for e in range(self.N_episodes): 
        for e in tqdm(range(self.N_episodes), disable=disable_tdqm): 
            
            #if not(e%100) and verbose:
            #    print( e,'/', self.N_episodes )

            ### we initialize the first state of the episode
            self.tree.reset_tree()
            if from_random : self.tree.random_maze()
            current_state = self.tree.Wall_state.sum() ### START state

            #sum the rewards that the agent gets from the environment
            total_episode_reward = 0

            for i in range(self.N_max_action): 
                ### we sample a float from a uniform distribution over 0 and 1
                # if the sampled float is less than the exploration proba
                #     the agent selects arandom action
                # else
                #     he exploits his knowledge using the bellman equation 

                if np.random.uniform(0,1) < self.exploration_proba:

                    action = self.__sample_action()
                else:
                    action = np.argmax(self.Q_table[current_state,:])

                # The environment runs the chosen action and returns
                # the next state, a reward and true if the epiosed is ended.
                next_state, reward, done = self.__step( action, current_state)
                
                # We update our Q-table using the Q-learning iteration
                self.Q_table[current_state, action] = (1-self.lr)*self.Q_table[current_state, action] + self.lr*(reward + self.discount*max(self.Q_table[next_state,:]))

                if( np.max( np.abs( self.Q_table ) ) >0 ):
                    self.Q_table =  self.Q_table / np.max( np.abs( self.Q_table ) )
                
                total_episode_reward = total_episode_reward + reward
                
                # If the episode is finished, we leave the for loop
                current_state = next_state
                if done:
                    #print( 'HERE WE BREAK' )
                    break
                
            #We update the exploration proba using exponential decay formula 
            self.exploration_proba = max(self.min_exploration_proba, np.exp(-self.exploration_decreasing_decay*e))
            self.total_rewards_episode[e] = total_episode_reward
            self.total_QV_episode[e] = np.sum(np.abs(self.Q_table))
            
    def generate(self, from_random=False, print_text=False):
        
        ### we initialize the first state of the episode
        
        self.tree.reset_tree()
        if from_random : self.tree.random_maze()
        current_state = self.tree.Wall_state.sum() ### START state

        #sum the rewards that the agent gets from the environment
        total_episode_reward = 0

        for i in range(self.N_max_action): 

            action = np.argmax(self.Q_table[current_state,:])

            # The environment runs the chosen action and returns
            # the next state, a reward and true if the epiosed is ended.
            next_state, reward, done = self.__step( action, current_state)

            total_episode_reward = total_episode_reward + reward
            # If the episode is finished, we leave the for loop

            current_state = next_state
            if done:
                break
            
        if print_text : print( 'Reward : ', total_episode_reward )
            
    def __sample_action( self ):
        return np.random.randint( self.N_action )
    
    def __step( self, action, current_state ):

        maze_state_before_action = self.tree.check() ### store before action state to compare with the post action one
        is_action_done = self.__do_action( action )  ### perform the action on the maze
        maze_state_after_action = self.tree.check()
        new_state = self.__get_state()
        reward = self.__get_reward( action, is_action_done, current_state, maze_state_before_action, maze_state_after_action )

        done = False
        if (action==self.tree.N_Wall) or not(maze_state_after_action):
            done = True

        return new_state, reward, done
    
    def __do_action( self, Wall_ID ):
        ### build or brake the wall
        ### return True if the action has been done
        if Wall_ID<self.tree.N_Wall: ### CONSTRUCTION
            if self.tree.Wall_state[Wall_ID] :
                return False ###Wall already built
            else :
                self.tree.build_WALL( Wall_ID )
                return True
        else : return True
            
    def __get_state(self):
        if 1:
            ### the status is the number of Walls build
            return self.tree.Wall_state.sum() 
        
    def __get_reward( self, action, is_action_done, current_state, maze_state_before_action, maze_state_after_action ):
    
        Reward=0
        ### reward for finishing a do-able maze
        if (action==self.tree.N_Wall) and maze_state_after_action:
            Reward += (2/self.tree.N_Wall) * self.tree.Wall_state.sum() 

        ### reward for having done a do-able action = build a wall
        if (action<self.tree.N_Wall) and is_action_done:
            Reward += 1 
        else : ### wall already build = non-doable action
            Reward += 0

        ### penality for braking the maze
        if not(maze_state_after_action):
            Reward += -2# self.tree.N_Wall/2 
            
        return Reward
