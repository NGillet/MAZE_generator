import numpy as np
import matplotlib.pyplot as plt

### Class to manage the MAZE grid, cells and walls

### The grid is represented in math matrix way
### X for the columns
### Y for the rows /!\ FROM TOP TO BOTTOM
### ---------------> X
### |
### |
### |     (X,Y)
### |
### |
### v
### Y

### Cell represent a grid cell, with its coordinates, and its neighbor 
### Cells can be adressed by their (XY) coordinates, or ID the 1D coordinates
### ID = X + N_grid*Y 

class Cell:
    def __init__(self, ID, N_grid):
        
        self.N_grid = N_grid
        self.ID = ID ### 1D coordinate of the cell 
        self.X, self.Y = self.get_XY_from_ID( ID )
        
        ### store each cell neighbors, for easier acces later
        self.voisines_ID  = []
        self.__get_voisines_ID()
        
        ### flag for special cells
        self.is_START = False
        self.is_OUT = False
        self.is_CHEST = False
        
        ### init for the tree structure
        self.next = []
        self.previous = []
        self.layer_ID = None
        
    def __get_voisines_ID(self):
        ### get and store neighbors cells
        ### in a list
        for direction in [0,1]:
            for offset in [-1,1]:
                
                if direction: ### X
                    X_voisine = offset+self.X
                    Y_voisine = self.Y
                else:         ### Y
                    X_voisine = self.X
                    Y_voisine = offset+self.Y
                         
                if (X_voisine<0)+(X_voisine==self.N_grid)+(Y_voisine<0)+(Y_voisine==self.N_grid) : 
                    ### boudary conditions
                    ### if the neighbor is outside the grid
                    continue
                else:
                    voisine_ID = self.get_ID_from_XY( [X_voisine,Y_voisine] )
                    self.voisines_ID.append( voisine_ID )
                    
    def get_XY_from_ID(self, ID):
        ### Coordinate transformation from 2D to 1D
        Y = ID//self.N_grid
        X = (ID-Y*self.N_grid)
        return X, Y

    def get_ID_from_XY(self, XY):
        ### Coordinate transformation from 1D to 2D
        return XY[0] + self.N_grid*XY[1]
    
###------------------------------------------------------------### 
    
### The maze grid is represented as a cell-tree
### the TOP cell is the STARTING cell of the maze
### all the cells are added to the chained list (or tree)
### added from top to bottom

### The tree structure in usefull to 'quickly' check if a path exist between the START and other cells (like OUT or CHEST) 
        
class Cell_Tree:
    def __init__(self, N_grid):
        
        self.N_grid = N_grid
        ### table to track if cells have been added in the tree
        self.__is_cell_in = np.zeros( self.N_grid**2, dtype=bool )
        
        ### First, init the START, OUT and CHEST cells
        self.__ID_cell_START = None ### store special cell ID for easy acces
        self.__ID_cell_OUT   = None
        self.__ID_cell_CHEST = None
        self.__init_MAZE() 
        
        ### init the first cell (head of the tree) = the START cell
        self.head = Cell(self.__ID_cell_START, N_grid)
        self.__is_cell_in[self.__ID_cell_START] = True 
        
        ### init the first layer
        ### layers represent the distance from the head (each layer has a different number of cells)
        ### it permits to loop over the cell 
        
        self.head.layer_ID = 1
        self.N_layer = 1
        self.layers = [[self.head]]
        ### generate the cell tree from the top layer (which contain only the START cell)
        self.__generate_chain( self.layers[0] )
                
        ### Finish to init the special cells
        self.cell_START = self.head
        self.cell_OUT   = self.get_cell( self.__ID_cell_OUT )
        self.cell_CHEST = self.get_cell( self.__ID_cell_CHEST )
        self.cell_START.is_START = True
        self.cell_OUT.is_OUT     = True
        self.cell_CHEST.is_CHEST = True
        
        ### 
        self.N_Wall = self.N_grid*(self.N_grid-1) *2
        self.Wall_state = np.zeros( self.N_Wall, dtype=bool )
###------------------------------------------------------------### 
### Tree management
###------------------------------------------------------------### 
    def __init_MAZE(self):
        ### Init the START, OUT and CHEST cells
        ### NOTE : - I impose that the OUT cell should be different than the START cell
        ###        - I impose START and OUT to be on side cells

        N_side = self.N_grid*2 + (self.N_grid-2)*2 ### number of cells on the side 
        ###IDs of cells on the side
        ID_side = np.concatenate((np.arange(self.N_grid),                      ### NORTH: Y=0, N_grid Xs
                (self.N_grid-1) + np.arange(1,self.N_grid)*self.N_grid,        ### EAST : X=N_grid-1, only N_grid-1 Ys
                np.arange(0,self.N_grid-1)[::-1]+ (self.N_grid-1)*self.N_grid, ### SOUTH: Y=N_grid-1, only N_grid-1 Xs
                np.arange(1,self.N_grid-1)[::-1]*self.N_grid,                  ### WEST: X=0, only N_grid-1-1 Xs
              ))
        
        while True: ### OUT should be different that START
            id_rand_startstop = np.random.randint(0,N_side,2) 
            if id_rand_startstop[0] != id_rand_startstop[1]:
                break

        self.__ID_cell_START = ID_side[id_rand_startstop[0]]
        self.__ID_cell_OUT   = ID_side[id_rand_startstop[1]]
        self.__ID_cell_CHEST = np.random.randint(0,self.N_grid**2)
        
    def __generate_chain(self, layer):
        ### Create the chained list of cells, from top (START) to bottom (!=OUT)
        ### The next cells are the neighbors that are 'bellow'
        
        ### The construction is recursive, layer after layer
        
        ### NOTE : one cell can be the next of several other cells 
        
        ### check if the chain is complete
        if self.__is_cell_in.sum()==self.N_grid**2 :
            return 0
        else:
            ### add, init a new layer
            self.N_layer += 1
            self.layers.append( [] )
            
            for current_cell_in_layer in layer:
                for voisine_ID in current_cell_in_layer.voisines_ID:
                    
                    ### check if cell_voisine is already in the tree
                    if self.__is_cell_in[voisine_ID] :    
                        cell_voisine = self.get_cell(voisine_ID)
                        
                        ### if cell_voisine is above then go next voisine 
                        if (cell_voisine.layer_ID<self.N_layer) :
                            continue
                        else:
                            ### cell voisine added to the curent cell next
                            current_cell_in_layer.next.append( cell_voisine ) 
                            ### but cell_voisine is not added AGAIN on the layer 
                            cell_voisine.previous.append( current_cell_in_layer )
                            
                    else: ### if cell_voisine is not in the tree 
                        cell_voisine = Cell( voisine_ID, self.N_grid )
                        self.__is_cell_in[voisine_ID] = True 
                        current_cell_in_layer.next.append( cell_voisine ) ### cell voisine added to the curent cell next
                        self.layers[ self.N_layer-1 ].append( cell_voisine ) ### cell voisine added to the next layers
                        cell_voisine.layer_ID = self.N_layer
                        cell_voisine.previous.append( current_cell_in_layer )
                    
            ### generate the next layer from the layer just build previously, until all cells are in the tree
            self.__generate_chain( self.layers[ self.N_layer-1 ] )
        
    def reset_tree(self):
        """
        Clean the maze 
        by rebuilding all cells
        by removing all the Walls
        NOTE that the special cells (START, OUT and CHEST) are not modified
        """
        self.__is_cell_in = np.zeros( self.N_grid**2, dtype=bool )
        
        self.head = Cell(self.__ID_cell_START, self.N_grid)
        self.__is_cell_in[self.__ID_cell_START] = True
        self.head.layer_ID = 1
        
        self.N_layer = 1
        self.layers = [[self.head]]
        self.__generate_chain( self.layers[0] )
        
        self.cell_START = self.head
        self.cell_OUT   = self.get_cell( self.__ID_cell_OUT )
        self.cell_CHEST = self.get_cell( self.__ID_cell_CHEST )
        self.cell_START.is_START = True
        self.cell_OUT.is_OUT     = True
        self.cell_CHEST.is_CHEST = True
        
        self.Wall_state = np.zeros( self.N_Wall, dtype=bool )
        
    def get_cell( self, ID ):
        """
        Return the cell (object) from its ID
        """
        ### all cells are checked from the layers of the tree
        for cell in self.__flat_listoflist( self.layers ):
            if cell.ID == ID:
                return cell
        return None
    
    def __flat_listoflist( self, listtoflat ):
        ### flat a list of list
        ### usefull to loop over all layers' cells
        return [item for sublist in listtoflat for item in sublist]
        
###------------------------------------------------------------### 
### Wall management

### NOTE : 
### Walls are manage in two parallel structure
### Walls are represented in the cell.next : 
###      - if the neibhbor cell is in next, theirfor there is no wall between the cells
###      - otherwise their is a wall
### By going to next to next we can explore all the accessible cell from START
###
### Walls are also reprensented by a bool table : Wall_state
### it just store if a wall is construct (True) or not (False)
### This table facilitates the access to the wall state (for plot for example) 

### ( It is dangerous because the 2 'structures' have to be sychronized )

### Walls can be through ID (1D) or from two neighbor cells IDs (ID1,ID2) 
###------------------------------------------------------------### 
        
    def build_WALL( self, Wall_ID ):
        """
        Remove a cell from the list of next cells
        It represent a "WALL CONSTRUCTION"
        """
        
        current_cell_ID, next_cell_ID = self.__from_WallID_to_CellID( Wall_ID )
        ### The order of cells is automatically chosen below
        ### it is important because the tree is "one-way"->"going down"
        
        current_cell = self.get_cell( current_cell_ID )
        next_cell = self.get_cell( next_cell_ID )
        
        if current_cell.layer_ID < next_cell.layer_ID:
            current_cell.next.remove( next_cell )
            next_cell.previous.remove( current_cell )
        else:
            next_cell.next.remove( current_cell )
            current_cell.previous.remove( next_cell )
        ### update the wall state
        self.Wall_state[Wall_ID] = not(self.Wall_state[Wall_ID]) ### change state of the wall : should be True
        if not(self.Wall_state[Wall_ID]) :
            print( '/!\ Wall_state not synchronized (build_WALL_between_cells)')
            
            
    def brake_WALL( self, Wall_ID ):
        """
        Add a cell from the list of next cells
        It represent a "WALL DESTRUCTION"
        """
        current_cell_ID, next_cell_ID = self.__from_WallID_to_CellID( Wall_ID )
        
        current_cell = self.get_cell( current_cell_ID )
        next_cell = self.get_cell( next_cell_ID )
        
        if current_cell.layer_ID < next_cell.layer_ID:
            current_cell.next.append( next_cell )
            next_cell.previous.append( current_cell )
        else:
            next_cell.next.append( current_cell )
            current_cell.previous.append( next_cell )
        ### update the wall state
        self.Wall_state[Wall_ID] = not(self.Wall_state[Wall_ID]) ### change state of the wall : should be False
        if self.Wall_state[Wall_ID] :
            print( '/!\ Wall_state not synchronized (brake_WALL_between_cells)')
                       
    def __from_WallID_to_CellID( self, Wall_ID ):
        ### Convert the WALL ID into Cells ID

        ### The first half is the HORIZONTAL WALLS, from top to bottom
        ### The second half is the VERTICAL WALLS, ffrom left to right

        if Wall_ID < (self.N_Wall/2) :
            return Wall_ID, Wall_ID+self.N_grid
        else: ### for the vertical wall the trik is to switch the X-Y axes
            Wall_ID_tmp = Wall_ID-(self.N_Wall//2)
            Y = Wall_ID_tmp//self.N_grid
            X = (Wall_ID_tmp-Y*self.N_grid)
            Wall_ID_tmp_2 = Y + X*self.N_grid ### new ID from switched axes
            return Wall_ID_tmp_2, Wall_ID_tmp_2+1
        
    def __from_CellID_to_WallID( self, current_cell_ID, next_cell_ID ):
        ### Convert the Cells IDs into  WALL ID

        min_ID = np.min( [current_cell_ID, next_cell_ID] ) 
        max_ID = np.max( [current_cell_ID, next_cell_ID] )
        
        if max_ID==(min_ID+self.N_grid): 
            return min_ID
        else:
            Y = min_ID//self.N_grid
            X = (min_ID-Y*self.N_grid)
            return Y+X*self.N_grid + (self.N_Wall//2)
        
    def random_maze(self):
        
        self.reset_tree()
        
        self.Wall_state = np.zeros( self.N_Wall, dtype=bool )
        
        Wall_to_build = np.random.randint(0,2,self.N_Wall).astype(bool)
        
        for Wall_ID, is_to_build in enumerate(Wall_to_build):
            if( is_to_build ) : self.build_WALL( Wall_ID )
            
###------------------------------------------------------------### 
### path management
###------------------------------------------------------------### 
       
    def check(self, verbose=0):
        """
        Check if the OUT cell is accessible from the START cell
        """
        check = True
        is_cell_checked = np.zeros( self.N_grid**2, dtype=bool )
        is_cell_checked[self.head.ID]=True
        check *= self.__check_if_cell_is_still_accessible( self.head.next, is_cell_checked, target_cell='is_OUT', verbose=verbose )
        is_cell_checked = np.zeros( self.N_grid**2, dtype=bool )
        is_cell_checked[self.head.ID]=True
        check *= self.__check_if_cell_is_still_accessible( self.head.next, is_cell_checked, target_cell='is_CHEST', verbose=verbose )
        return bool(check)
    
    def __check_if_cell_is_still_accessible( self, next_cells, is_cell_checked, target_cell='is_OUT', count=1, verbose=0 ):
        """
        Go from next to next, from START until it find OUT, or reach the bottom
        return a bool True if OUT is found
        
        The search is done recursivelly, from the next list
        The next_next_cells list is build to feed the next search
        
        count : count the number of time it get into the recursive loop^: for debug
        """
        
        if verbose : 
            print( 'Count : ', count )  
            print( 'Cell already check : ', np.where(is_cell_checked)[0] )  
            for cell in next_cells:
                print( cell.ID ) 
    
        next_next_cells = []
        next_next_cells_IDs = []

        ### loop to gather all the next next cells
        
        #getattr(tree.head,'is_OUT')
        
        for cell in next_cells:
            if getattr(cell,target_cell): ### OUT is found
                return True
            #print('la',cell.next)
            
            #print( cell.next, cell.previous )
            
            ### if their are no next cells, we have to look at the preivious one
            #if (cell.next==[]) or (is_cell_checked[cell.next[0].ID]) : 
            ### if a previous not already checked
            for cell_previous in cell.previous: ### check is the previous cell is already in the next_cells table 
                if not(is_cell_checked[cell_previous.ID]):
                    next_next_cells.append( [cell_previous] )
                    next_next_cells_IDs.append( [cell_previous.ID] )
            else : 
                for cell_next in cell.next:
                    if not(is_cell_checked[cell_next.ID]):
                        next_next_cells.append( [cell_next] )
                        next_next_cells_IDs.append( [cell_next.ID] )
                
        next_next_cells = np.array( [item for sublist in next_next_cells for item in sublist] )
        next_next_cells_IDs = [item for sublist in next_next_cells_IDs for item in sublist]

        if next_next_cells_IDs==[]: ### the bottom of the tree is reach
            return False

        for cell in next_cells:
            is_cell_checked[cell.ID] = True  
        
        ### The list of next_next have to be cleaned from multiple occurences
        next_next_cells_IDs, ID_i_sorted = np.unique(next_next_cells_IDs, return_index=True)
        next_next_cells = next_next_cells[ID_i_sorted]

        count+=1
        ###not realy sure what I am doing here
        ###I have to do that to extract the return the deepest check
        if not( self.__check_if_cell_is_still_accessible( next_next_cells, is_cell_checked, target_cell=target_cell, count=count, verbose=verbose ) ):
            return False
        else:
            return True
        
###------------------------------------------------------------### 
### plot management
###------------------------------------------------------------###         
        
    def plot_grid( self, figAndAxes=None ):

        if figAndAxes is None:
            fig, axes = plt.subplots()
        else:
            fig, axes = figAndAxes

        axes.vlines( np.arange(1,self.N_grid)-0.5, -0.5, self.N_grid-0.5, 'k', ls=':', alpha=0.5)
        axes.hlines( np.arange(1,self.N_grid)-0.5, -0.5, self.N_grid-0.5, 'k', ls=':', alpha=0.5)

        axes.vlines( np.array([0,self.N_grid])-0.5, -0.5, self.N_grid-0.5, 'k')
        axes.hlines( np.array([0,self.N_grid])-0.5, -0.5, self.N_grid-0.5, 'k')

        x0,x1 = axes.get_xlim()
        y0,y1 = axes.get_ylim()
        axes.set_aspect( (x1-x0)/(y1-y0) )

        plt.gca().invert_yaxis()

        return fig, axes

    def plot_inoutchest( self, figAndAxes=None ):

        if figAndAxes is None:
            fig, axes = plt.subplots()
        else:
            fig, axes = figAndAxes
        axes.text( self.cell_START.X-0.2, self.cell_START.Y, 'START', c='r' )
        axes.text( self.cell_OUT.X-0.2, self.cell_OUT.Y  , 'OUT'  , c='r' )
        axes.text( self.cell_CHEST.X-0.2, self.cell_CHEST.Y, 'CHEST', c='r' )

        return fig, axes
    
    def plot_Walls(self, figAndAxes=None ): 
        if figAndAxes is None:
            fig, axes = plt.subplots()
        else:
            fig, axes = figAndAxes
        Wall_to_Draw = np.where( self.Wall_state )[0]    
        for Wall_ID in Wall_to_Draw:
            Xs, Ys = self._from_WallID_to_plot( Wall_ID ) 
            axes.plot( Xs, Ys, 'k' )
        return figAndAxes
    
    def _from_WallID_to_plot(self, Wall_ID ):
        ### Convert the WALL ID into plot coordinates

        ### The first half is the HORIZONTAL WALLS, from top to bottom
        ### The second half is the VERTICAL WALLS, from left to right
        if Wall_ID < (self.N_Wall/2) :
            Y = Wall_ID//self.N_grid
            X = (Wall_ID-Y*self.N_grid)
            return [X-0.5,X+0.5], [Y+0.5,Y+0.5]

        else: ### for the vertical wall the trik is to switch the X-Y axes
            Wall_ID_tmp = Wall_ID-(self.N_Wall//2)
            Y = Wall_ID_tmp//self.N_grid
            X = (Wall_ID_tmp-Y*self.N_grid)
            Wall_ID_tmp_2 = Y + X*self.N_grid ### new ID from switched axes
            Y = Wall_ID_tmp_2//self.N_grid
            X = (Wall_ID_tmp_2-Y*self.N_grid)
            return [X+0.5,X+0.5], [Y-0.5,Y+0.5]

    def visu( self ):
        """
        Plot the actual state of the maze
        """
        figAndAxes = self.plot_grid( figAndAxes=None )
        self.plot_inoutchest( figAndAxes=figAndAxes )
        self.plot_Walls( figAndAxes=figAndAxes )
        return figAndAxes