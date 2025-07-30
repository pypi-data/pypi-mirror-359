import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.manifold import MDS
from scipy.spatial.distance import cdist, pdist, squareform
from scipy import ndimage

class RFTreeAnalyzer:
    """
    a class to analyze individual trees in a RF model
    and extract their properties including but not limited to strength estimates
    """
    
    def __init__(self, rf_model, X_train, y_train, X_test=None, y_test=None):
        self.rf_model = rf_model
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.n_trees = rf_model.n_estimators
        self.tree_properties = {}
        
    def extract_single_tree_properties(self, tree_idx):
        """
        get properties of a single tree from the forest model
        """
        if tree_idx >= self.n_trees:
            raise ValueError(f"tree index {tree_idx} exceeds forest size {self.n_trees}") #asked for tree does not exist in forest
        
        # gets tree number tree_idx
        tree = self.rf_model.estimators_[tree_idx]
        
        # bootstrap samples used for this tree
        bootstrap_indices = self.rf_model.estimators_samples_[tree_idx]
        oob_indices = np.setdiff1d(np.arange(len(self.X_train)), bootstrap_indices)#gives oob indices by seeing which indices
        #are not in the bootstrap indices used for training the tree
        
        # tree-specific metrics:
        properties = {
            'tree_index': tree_idx,
            'tree_depth': tree.tree_.max_depth,
            'n_nodes': tree.tree_.node_count,
            'n_leaves': tree.tree_.n_leaves,
            'bootstrap_sample_size': len(bootstrap_indices),
            'oob_sample_size': len(oob_indices),
            'feature_importances': tree.feature_importances_
        }
        
        # OOB error tree tree_idx (tree strength indicator)
        if len(oob_indices) > 0:
            X_oob = self.X_train[oob_indices]
            y_oob = self.y_train[oob_indices]
            
            # predictions from tree tree_idx
            tree_predictions = tree.predict(X_oob)
            
            # calculate error based on problem type
            if hasattr(self.rf_model, 'classes_'):  # classification case
                oob_accuracy = accuracy_score(y_oob, tree_predictions) #comes out as percentage (normalize = False)
                oob_error = 1 - oob_accuracy # % oob error 
                properties['oob_accuracy'] = oob_accuracy
            else:  # regression case
                oob_mse = mean_squared_error(y_oob, tree_predictions)
                properties['oob_mse'] = oob_mse
                oob_error = oob_mse
            
            properties['oob_error'] = oob_error
            properties['tree_strength'] = 1 / (1 + oob_error)  # tree_strength calculation! inverse relationship
        else:
            properties['oob_error'] = np.nan
            properties['tree_strength'] = np.nan
        
        return properties
    
    def analyze_all_trees(self):
        """
        analyze all trees in a rf_model
        """
        all_properties = []
        
        for i in range(self.n_trees):#all trees
            props = self.extract_single_tree_properties(i)#extracts all of i-th tree's properties
            all_properties.append(props)#adds it to 'all_properties'
            
        self.tree_properties = pd.DataFrame(all_properties)#dataframes it up
        return self.tree_properties#all my tree properties of my forest are in here
    
    def calculate_tree_correlations(self, sample_size=1000):
        """
        returns correlation between individual trees' predictions
        """
        if self.X_test is not None:
            X_sample = self.X_test[:sample_size]#takes sample from testing dataset if it exists
        else:
            # otherwise uses a random sample from training data
            sample_indices = np.random.choice(len(self.X_train), 
                                            min(sample_size, len(self.X_train)), 
                                            replace=False)#takes random sample indices
            X_sample = self.X_train[sample_indices]#extracts samples from random sample indices
        
        # predicts on the sample data with each tree 
        tree_predictions = np.array([
            tree.predict(X_sample) for tree in self.rf_model.estimators_
        ])
        
        # correlation matrix
        correlation_matrix = np.corrcoef(tree_predictions)
        
        return correlation_matrix
    
    def get_tree_summary_stats(self):
        """
        summary statistics for all tree properties
        """
        if self.tree_properties is None or len(self.tree_properties) == 0:
            self.analyze_all_trees()
        
        summary = {
            'mean_tree_strength': self.tree_properties['tree_strength'].mean(),
            'std_tree_strength': self.tree_properties['tree_strength'].std(),
            'mean_oob_error': self.tree_properties['oob_error'].mean(),
            'std_oob_error': self.tree_properties['oob_error'].std(),
            'mean_tree_depth': self.tree_properties['tree_depth'].mean(),
            'mean_n_nodes': self.tree_properties['n_nodes'].mean(),
            'mean_n_leaves': self.tree_properties['n_leaves'].mean()
        }
        print(f"\n=== SUMMARY STATISTICS ===")
        for key, value in summary.items():
            print(f"{key}: {value:.4f}")
        return self.tree_properties

def demonstrate_single_tree_analysis():
    """
    demonstrates analysis on one single tree
    """
    # sample data
    X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, 
                              n_redundant=2)#X features, y response var.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)#splits data into test (30%) and train
    
    # RF_model
    rf = RandomForestClassifier(n_estimators=100, 
                               bootstrap=True, oob_score=True)#create with 'n_estimators' trees
    rf.fit(X_train, y_train)#train
    
    # initialize RFTreeAnalyzer
    analyzer = RFTreeAnalyzer(rf, X_train, y_train, X_test, y_test)
    
    # analyze a single tree
    tree_id = 0#first tree in the set
    single_tree_props = analyzer.extract_single_tree_properties(tree_id)#tree 'tree_id' analyzed here
    
    print(f"=== SINGLE TREE ANALYSIS (tree n°{tree_id+1}) ===")
    for key, value in single_tree_props.items():
        if isinstance(value, np.ndarray):
            print(f"{key}: array of shape {value.shape}")
        else:
            print(f"{key}: {value}")
    
    print(f"\n=== OVERALL FOREST OOB SCORE ===")
    print(f"forest OOB Score: {rf.oob_score_:.4f}")
    
    return analyzer, single_tree_props, rf.oob_score_, rf


###########################
###END OF RFTreeAnalyzer###
###########################



def create_2d_gaussian(size, sigma=1.0):
    """creates a 2D Gaussian kernel for convolution"""
    x = np.arange(size) - size // 2
    y = np.arange(size) - size // 2
    X, Y = np.meshgrid(x, y)
    gaussian = np.exp(-(X**2 + Y**2) / (2 * sigma**2))
    return gaussian / np.sum(gaussian)

def position_trees_2d(correlations, tree_strengths,
                      grid_size=300, rmin=1.5,
                      rmax=50, ring_width=1,
                      gaussian_sigma=0.2):
    """
    positioning trees in 2D space using a similar position voting algorithm as in the literature
    
    parameters:
    -----------
    correlations : np.array
        tree correlation matrix
    tree_strengths : np.array  
        tree strength values
    grid_size : int
        size/resolution of the 2D voting grid | highly dependent on amount of trees. computationally expensive
    rmin : float
        min distance between trees
    rmax : float  
        max distance for ring placement
    ring_width : float
        width of the voting rings
    gaussian_sigma : float
        smoothing
    """
    
    n_trees = len(tree_strengths)
    
    # Sort trees by strength (strongest first)
    tree_order = np.argsort(-tree_strengths)  # Negative for descending order
    print(f"tree order:{tree_order}")
    # Initialize voting spaces for each tree
    voting_spaces = {i: np.zeros((grid_size, grid_size)) for i in range(n_trees)}
    
    # Store final positions
    positions = np.zeros((n_trees, 2))
    
    # Create coordinate grids
    x_coords = np.arange(grid_size)
    y_coords = np.arange(grid_size)
    X, Y = np.meshgrid(x_coords, y_coords)
    
    # Gaussian kernel for convolution
    gaussian_kernel = create_2d_gaussian(int(6 * gaussian_sigma), gaussian_sigma)
    
    print(f"processing {n_trees} trees in order of strength...")
    
    for i, current_tree_idx in enumerate(tree_order):
        print(f"processing tree... ({i+1}/{n_trees})")
        
        if i == 0:
            # First tree goes to center
            pos_x, pos_y = grid_size // 2, grid_size // 2
            #print(f"  Placed at center: ({pos_x}, {pos_y})")
        else:
            # Find position with maximum votes
            voting_space = voting_spaces[current_tree_idx]
            max_vote_idx = np.unravel_index(np.argmax(voting_space), voting_space.shape)
            pos_y, pos_x = max_vote_idx  # Note: numpy arrays are (row, col) = (y, x)
            #print(f"  Placed at max vote position: ({pos_x}, {pos_y}), vote value: {voting_space[max_vote_idx]:.4f}")
        
        positions[current_tree_idx] = [pos_x, pos_y]
        
        # Update voting spaces for all remaining unplaced trees
        remaining_trees = tree_order[i+1:]  # Trees not yet placed
        
        for other_tree_idx in remaining_trees:
            # Get correlation between current tree and other tree
            correlation = correlations[current_tree_idx, other_tree_idx]
            
            # Calculate desired distance based on correlation (Equation 10)
            desired_distance = (1 - correlation) * rmax + rmin
            
            # Create ring around current tree position (Equation 9)
            distances = np.sqrt((X - pos_x)**2 + (Y - pos_y)**2)
            ring_mask = np.abs(distances - desired_distance) < ring_width
            
            # Convert ring to voting contribution
            vote_contribution = ring_mask.astype(float)
            
            # Apply Gaussian smoothing (convolution)
            if np.any(vote_contribution):
                vote_contribution = ndimage.convolve(vote_contribution, gaussian_kernel, mode='constant')
            
            # Add to voting space
            voting_spaces[other_tree_idx] += vote_contribution
            
            #print(f"    Updated votes for tree {other_tree_idx} (correlation: {correlation:.3f}, desired_dist: {desired_distance:.2f})")
    
    return positions, voting_spaces, tree_order

def add_jitter_to_positions(positions, jitter_strength=0.3):
    """adds tiny random offset to overlapping positions"""
    
    jittered_positions = positions.copy().astype(float)
    
    # find overlapping positions first
    position_groups = defaultdict(list)
    for i, pos in enumerate(positions):
        position_groups[tuple(pos)].append(i)
    
    # add jitter_strength jitter to overlapping positions
    for pos_tuple, tree_indices in position_groups.items():
        if len(tree_indices) > 1:
            #print(f"adding jitter to {len(tree_indices)} trees at position {pos_tuple}")
            
            n_overlapping = len(tree_indices)#number of overlapping trees
            jitter_x = np.random.normal(0, jitter_strength, n_overlapping)#gaussian jitter array for the x-axis
            jitter_y = np.random.normal(0, jitter_strength, n_overlapping)#gaussian jitter array for the y-axis
            
            # apply jitter
            for j, tree_idx in enumerate(tree_indices):
                jittered_positions[tree_idx, 0] += jitter_x[j]#applies j-th gaussian jitter for overlapping tree number tree_idx
                jittered_positions[tree_idx, 1] += jitter_y[j]
    
    return jittered_positions


def analyze_positioning_quality(positions, correlations):
    """analyzes how well the positioning preserves correlations"""
    
    # pairwise distances in 2D space
    spatial_distances = cdist(positions, positions)
    
    # convert correlations to distances (higher correlation = smaller distance)
    correlation_distances = 1 - np.abs(correlations)
    
    # upper triangle indices (without diagonal and duplicates)
    triu_indices = np.triu_indices_from(correlations, k=1)

    spatial_dist_vec = spatial_distances[triu_indices]
    corr_dist_vec = correlation_distances[triu_indices]
    
    # calculate correlation between spatial and correlation distances
    # (negative correlation means high tree correlation = small spatial distance)
    layout_quality = np.corrcoef(spatial_dist_vec, corr_dist_vec)[0, 1]
    
    print(f"layout quality (correlation preservation): {layout_quality:.4f}")
    print(f"higher values = better preservation of correlation structure")
    
    return layout_quality, spatial_dist_vec, corr_dist_vec






def visualize_tree_positions1D(positions, tree_strengths):
    """
    first step in visualizing the whole forest: visualizing individual tree strengths and their correlations
    in other words: how strong is each individual tree and what are their relationships

    'barcode' style plotting of trees.
    each line represents a tree and distances between trees depend on their correlation (close trees have higher oob-prediction correlations)
    tree alpha shows that individual tree's strength (low alpha = low strength)
    """
    
    distances_2d = squareform(pdist(positions))
    
    # 1D MDS
    mds = MDS(n_components=1, dissimilarity='precomputed', 
              max_iter=1000, eps=1e-6) # n_components = 1 > 1-dimensional
    
    barcode_coords = mds.fit_transform(distances_2d) #coordinates of trees in 1D
    
    print(f"MDS stress value: {mds.stress_:.4f}")
    #print(f"1D coords. range: {barcode_coords.min():.2f} to {barcode_coords.max():.2f}")

    
    # normalize tree strengths to 0-1 range for alpha values
    normalized_strengths = (tree_strengths - tree_strengths.min()) / (tree_strengths.max() - tree_strengths.min()) # lowest value gets alpha = 0 > problem
    # ensure at least minimal visibility to solve previous visualization issue
    normalized_strengths = normalized_strengths * 0.8 + 0.2  # scales alpha values to 0.2-1.0 range
    
    # plotting with a 'barcode'-like visual aesthetic
    fig, ax = plt.subplots(figsize=(16, 4))#16:4 barcode ratio
    
    # black background for a more pleasant & artistic aesthetic
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # vertical white lines with individual alpha values
    for i, (x_val, strength) in enumerate(zip(barcode_coords, normalized_strengths)):
        ax.axvline(x=x_val, color='white', alpha=strength, linewidth=1)
    
    # remove all text, labels, ticks, and grid for a more pleasant & artistic aesthetic
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title('')
    
    # remove axis borders
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # limits
    ax.set_ylim(0, 1)
    
    # remove any padding/margins
    plt.tight_layout()
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.canvas.manager.set_window_title('mycelium_forest')#title it the package name
    plt.show()
    
    return fig, ax

def run_tree_positioning_barcode(correlations, forest_df, forest_strength, resolution = 300):
    """
    main function to run the tree positioning algorithm
    
    parameters:
    -----------
    correlations: np.array
        correlation matrix of trees' oob predictions
    forest_df: pd.DataFrame  
        dataframe with trees' properties (contains 'tree_strength' column)
    forest_strength : float, optional
        overall (mean) forest out-of-bag strength calculated by using oob samples to determine a generalization score
    rf_model: RandomForestClassifier
        RF model
    max_branch_depth: integer
        maximum branch depth to visualize
    """
    tree_strengths = forest_df['tree_strength'].values#all tree strength values used as alpha values in the 'barcode'-like plot

    # positioning algorithm more or less following the literature
    # Hänsch, R., & Hellwich, O. (2015). Performance assessment and interpretation of random forests by three-dimensional visualizations.
    positions, voting_spaces, tree_order = position_trees_2d(
        correlations, tree_strengths,
        grid_size=resolution, rmin=1.5, rmax=50, ring_width=1, gaussian_sigma=0.2
    )# depending on positioning resolution (grid_size) and number of trees, some trees may find themselves overlapping in 2D space
    
    # visualizing results
    jittered_positions = add_jitter_to_positions(positions, jitter_strength=0.5)
    quality, _, _ = analyze_positioning_quality(positions, correlations)
    
    #barcode-viz
    fig, ax = visualize_tree_positions1D(jittered_positions, tree_strengths)# 'barcode' style plotting of trees
    
    return jittered_positions, voting_spaces, tree_order, quality, None















def calculate_deepest_branch_point(all_trees_structure, level_params, trunk_height=1.0):
    """
    calculates the deepest y-coordinate that any branch will reach
    """
    deepest_y = trunk_height
    
    def traverse_tree_depth(node, current_y, depth=0):#starts at root node
        nonlocal deepest_y
        
        if node is None or depth >= len(level_params):
            return current_y
        
        # if node has information & children, then it has branches
        if (node['information_gain'] > 0 and 
            node['left_child'] and node['right_child'] and 
            depth < len(level_params)):
            
            # where do branches end for this level?
            branch_height = level_params[depth]['branch_height']
            branch_end_y = current_y - branch_height
            
            # update deepest_y
            deepest_y = min(deepest_y, branch_end_y)
            
            # recursively check children
            if node['left_child']:
                traverse_tree_depth(node['left_child'], branch_end_y, depth + 1)
            if node['right_child']:
                traverse_tree_depth(node['right_child'], branch_end_y, depth + 1)
    
    #do this for all trees
    for tree_data in all_trees_structure:
        if tree_data['structure']:
            traverse_tree_depth(tree_data['structure'], 0)  # start from trunk bottom (y=0)
    
    return deepest_y


def extract_tree_structure_recursive(tree, max_depth=3):
    """
    extract tree structure information up to max_depth levels
    """
    tree_structure = tree.tree_
    
    def get_node_info(node_id, current_depth=0):
        if current_depth >= max_depth or node_id == -1:
            return None
            
        node_info = {
            'node_id': node_id,
            'depth': current_depth,
            'impurity': tree_structure.impurity[node_id],
            'n_samples': tree_structure.n_node_samples[node_id],
            'information_gain': 0.0,
            'left_child': None,
            'right_child': None,
            'left_weight': 0.0,
            'right_weight': 0.0
        }
        
        left_child_id = tree_structure.children_left[node_id]
        right_child_id = tree_structure.children_right[node_id]
        
        #if not leaf node, calculate information gain and recurse
        if left_child_id != right_child_id:  # not leaf node
            # calculates IG
            left_impurity = tree_structure.impurity[left_child_id]
            right_impurity = tree_structure.impurity[right_child_id]
            left_n_samples = tree_structure.n_node_samples[left_child_id]
            right_n_samples = tree_structure.n_node_samples[right_child_id]
            
            left_weight = left_n_samples / node_info['n_samples']
            right_weight = right_n_samples / node_info['n_samples']
            
            weighted_child_impurity = left_weight * left_impurity + right_weight * right_impurity
            node_info['information_gain'] = node_info['impurity'] - weighted_child_impurity
            node_info['left_weight'] = left_weight
            node_info['right_weight'] = right_weight
            
            # recursively get info for children
            node_info['left_child'] = get_node_info(left_child_id, current_depth + 1)
            node_info['right_child'] = get_node_info(right_child_id, current_depth + 1)
        
        return node_info
    
    return get_node_info(0)  # start from root (index 0)

def get_all_trees_structure(rf_model, max_depth=3):
    """
    Extract structure information for all trees up to max_depth
    """
    all_trees_structure = []
    
    for i, tree in enumerate(rf_model.estimators_):
        tree_structure = extract_tree_structure_recursive(tree, max_depth)
        all_trees_structure.append({
            'tree_index': i,
            'structure': tree_structure
        })
    
    return all_trees_structure
def draw_recursive_branches(ax, x_pos, y_pos, node_info, strength, 
                          coord_range, level_params, current_depth=0,
                          color_left_branch = "white", color_right_branch = "white"):
    """
    recursively draw branches for a tree node and its children
    """
    if node_info is None or current_depth >= len(level_params):
        return
    
    params = level_params[current_depth]
    
    # draw branch if there's information gain
    if node_info['information_gain'] > 0 and node_info['left_child'] and node_info['right_child']:
        
        #calculate branch width based on normalized information gain for this node
        normalized_ig = node_info.get('normalized_ig', 0)  # use node's normalized IG
        branch_width = normalized_ig * params['max_width'] * coord_range
        
        # branch position
        branch_length = branch_width
        
        left_x = x_pos - branch_length
        right_x = x_pos + branch_length
        branch_y_end = y_pos - params['branch_height']
        
        # alpha for this depth
        depth_alpha = strength * params['alpha_factor']
        
        #left branch
        ax.plot([x_pos, left_x], [y_pos, branch_y_end], 
               color=color_left_branch, alpha=depth_alpha, linewidth=params['line_width'])
        
        #right branch
        ax.plot([x_pos, right_x], [y_pos, branch_y_end], 
               color=color_right_branch, alpha=depth_alpha, linewidth=params['line_width'])
        
        # draw children branches
        if current_depth + 1 < len(level_params):
            draw_recursive_branches(ax, left_x, branch_y_end, node_info['left_child'], 
                                  strength, coord_range, level_params, current_depth + 1,
                                  color_left_branch = color_left_branch, color_right_branch = color_right_branch)
            draw_recursive_branches(ax, right_x, branch_y_end, node_info['right_child'], 
                                  strength, coord_range, level_params, current_depth + 1,
                                  color_left_branch = color_left_branch, color_right_branch = color_right_branch)

def visualize_tree_positions1D_multilevel(positions, tree_strengths, rf_model, 
                                        max_branch_depth=25, trunk_height=0.1,
                                        base_branch_height=0.08, base_max_width=0.05,
                                        base_branch_angle=45,color_trunk="white",color_left_branch="white",
                                        color_right_branch="white", auto_show=True):
    """
    RF visualization with multi-depth information gain-based branching
    """
    
    # 1D coordinates of trees
    distances_2d = squareform(pdist(positions))
    mds = MDS(n_components=1, dissimilarity='precomputed', 
              max_iter=1000, eps=1e-6)
    barcode_coords = mds.fit_transform(distances_2d).flatten()
    coord_range = barcode_coords.max() - barcode_coords.min()
    
    # get trees' structure
    all_trees_structure = get_all_trees_structure(rf_model, max_branch_depth)
    
    # normalizing tree strength for alpha values
    normalized_strengths = (tree_strengths - tree_strengths.min()) / (tree_strengths.max() - tree_strengths.min())
    normalized_strengths = normalized_strengths * 0.8 + 0.2
    
    # creating the plot
    total_depth = trunk_height + (base_branch_height * max_branch_depth)
    fig, ax = plt.subplots(figsize=(16, 6))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # plotting parameters for each level
    level_params = []
    for depth in range(max_branch_depth):
        depth_factor = 0.7 ** depth
        
        level_params.append({
            'branch_height': base_branch_height * depth_factor,
            'max_width': base_max_width * depth_factor,
            'branch_angle': base_branch_angle,
            'alpha_factor': 1.0 * (0.8 ** depth),
            'line_width': max(0.5, 1.0 * depth_factor),
        })
    

    # calculating the deepest point any branch will reach to better crop the plot
    deepest_y = calculate_deepest_branch_point(all_trees_structure, level_params, trunk_height)

    # assigns normalized IG to all nodes in a tree
    def assign_normalized_ig_to_tree(root_node):
        # collect all IG values within this tree only
        tree_igs = []
        
        def collect_tree_igs(node):
            if node is None:
                return
            tree_igs.append(node['information_gain'])
            if node['left_child']:
                collect_tree_igs(node['left_child'])
            if node['right_child']:
                collect_tree_igs(node['right_child'])
        
        collect_tree_igs(root_node)  #get all IGs for this specific tree
        
        # normalization parameters for this tree
        if len(tree_igs) > 0:
            min_tree_ig = min(tree_igs)
            max_tree_ig = max(tree_igs)
            tree_range = max_tree_ig - min_tree_ig
        else:
            tree_range = 0
        
        # apply normalization to all nodes in this tree
        def normalize_node(node):
            if node is None:
                return
            
            if tree_range > 0:
                node['normalized_ig'] = (node['information_gain'] - min_tree_ig) / tree_range
            else:
                node['normalized_ig'] = 0.5  # all splits equal in this tree
            
            if node['left_child']:
                normalize_node(node['left_child'])
            if node['right_child']:
                normalize_node(node['right_child'])
        
        normalize_node(root_node)
    

    # draw trees
    for i, (tree_data, x_val, strength) in enumerate(zip(all_trees_structure, barcode_coords, normalized_strengths)):
        
        # trunk params
        trunk_bottom = 0
        trunk_top = trunk_height#length of the root branch (=trunk)
        ax.plot([x_val, x_val], [trunk_bottom, trunk_top], 
               color=color_trunk, alpha=strength, linewidth=1)
        
        # assign normalized IG values to tree_data's nodes
        if tree_data['structure']:
            assign_normalized_ig_to_tree(tree_data['structure'])
            
            # drawing recursive branches starting from trunk bottom (y=0)
            draw_recursive_branches(ax, x_val, trunk_bottom, tree_data['structure'], 
                                  strength, coord_range, level_params,
                                  color_left_branch = color_left_branch, color_right_branch = color_right_branch)
    
    # set plot limits and clean up
    x_margin = coord_range * 0.05
    y_bottom = deepest_y - 0.05  # y lim just below the deepest branch
    y_top = trunk_height + 0.05
    
    ax.set_xlim(barcode_coords.min() - x_margin, barcode_coords.max() + x_margin)
    ax.set_ylim(y_bottom, y_top)
    
    # remove all other visual elements for aesthetic purposes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title('')
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    fig.canvas.manager.set_window_title('mycelium_forest')#title it the package name

    if auto_show:
        plt.show()
    
    return fig, ax, barcode_coords, all_trees_structure


def run_tree_positioning(correlations, forest_df, rf_model, forest_strength = None, max_branch_depth=25, resolution = 300, **viz_params):
    """
    main function to run the tree positioning algorithm
    
    parameters:
    -----------
    correlations: np.array
        correlation matrix of trees' oob predictions
    forest_df: pd.DataFrame  
        dataframe with trees' properties (contains 'tree_strength' column)
    forest_strength : float, optional
        overall (mean) forest out-of-bag strength calculated by using oob samples to determine a generalization score
    rf_model: RandomForestClassifier
        RF model
    max_branch_depth: integer
        maximum branch depth to visualize
    """
    
    tree_strengths = forest_df['tree_strength'].values
    
    positions, voting_spaces, tree_order = position_trees_2d(
        correlations, tree_strengths,
        grid_size=resolution,
        rmin=1.5, rmax=50, ring_width=1, gaussian_sigma=0.2
    )
    
    jittered_positions = add_jitter_to_positions(positions, jitter_strength=0.5)
    quality, spatial_dists, corr_dists = analyze_positioning_quality(positions, correlations)
    
    fig, ax, coords, tree_structures = visualize_tree_positions1D_multilevel(
        jittered_positions, tree_strengths, rf_model, 
        max_branch_depth=max_branch_depth,
        **viz_params  
    )
    
    return jittered_positions, voting_spaces, tree_order, quality, tree_structures









def visualize_tree_positions_circular(positions, tree_strengths, rf_model, 
                                    max_branch_depth=25, trunk_length=1.0,
                                    base_branch_length=0.6, base_max_angle=15,
                                    base_branch_angle=45, center_radius=0.2,
                                    color_trunk="white", color_left_branch="white",
                                    color_right_branch="white", auto_show=True):
    """
    circularvisualization with radial trees and angular branching
    """
    
    # same as linear method
    distances_2d = squareform(pdist(positions))
    mds = MDS(n_components=1, dissimilarity='precomputed', 
              max_iter=1000, eps=1e-6)
    barcode_coords = mds.fit_transform(distances_2d).flatten()
    
    # mapping 1D coordinates to angles (0 to 2pi)
    coord_min, coord_max = barcode_coords.min(), barcode_coords.max()
    coord_range = coord_max - coord_min if coord_max > coord_min else 1
    angles = 2 * np.pi * (barcode_coords - coord_min) / coord_range
    

    all_trees_structure = get_all_trees_structure(rf_model, max_branch_depth)
    

    normalized_strengths = (tree_strengths - tree_strengths.min()) / (tree_strengths.max() - tree_strengths.min())
    normalized_strengths = normalized_strengths * 0.8 + 0.2
    

    level_params = []
    for depth in range(max_branch_depth):
        depth_factor = 0.7 ** depth
        
        level_params.append({
            'branch_length': base_branch_length * depth_factor,  # radial extension
            'max_angle': base_max_angle * depth_factor,          # angular spread (in degrees)
            'alpha_factor': 1.0 * (0.8 ** depth),
            'line_width': max(0.5, 1.0 * depth_factor),
        })
    

    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    def assign_normalized_ig_to_tree(root_node):
        # collect all IG values within this tree only
        tree_igs = []
        
        def collect_tree_igs(node):
            if node is None:
                return
            tree_igs.append(node['information_gain'])
            if node['left_child']:
                collect_tree_igs(node['left_child'])
            if node['right_child']:
                collect_tree_igs(node['right_child'])
        
        collect_tree_igs(root_node)  # get all IGs for this specific tree
        
        #normalization parameters for this tree
        if len(tree_igs) > 0:
            min_tree_ig = min(tree_igs)
            max_tree_ig = max(tree_igs)
            tree_range = max_tree_ig - min_tree_ig
        else:
            tree_range = 0
        
        #normalization to all nodes in this tree
        def normalize_node(node):
            if node is None:
                return
            
            if tree_range > 0:
                node['normalized_ig'] = (node['information_gain'] - min_tree_ig) / tree_range
            else:
                node['normalized_ig'] = 0.5  #all splits equal
            
            if node['left_child']:
                normalize_node(node['left_child'])
            if node['right_child']:
                normalize_node(node['right_child'])
        
        normalize_node(root_node)
    

    # drawing trees
    max_radius = center_radius + trunk_length + sum(p['branch_length'] for p in level_params)
    
    for i, (tree_data, angle, strength) in enumerate(zip(all_trees_structure, angles, normalized_strengths)):
        
        # main trunks
        trunk_start = center_radius
        trunk_end = center_radius + trunk_length
        ax.plot([angle, angle], [trunk_start, trunk_end], 
               color=color_trunk, alpha=strength, linewidth=1)
        
        if tree_data['structure']:
            assign_normalized_ig_to_tree(tree_data['structure'])
            
            draw_circular_branches(ax, angle, trunk_end, tree_data['structure'], 
                                 strength, level_params, current_depth=0,
                                 color_left_branch = color_left_branch, color_right_branch = color_right_branch)
    
    # polar plot
    ax.set_ylim(0, max_radius-0.05) # 0.05 margin is subjective
    ax.set_theta_zero_location('N')  # 0 degrees at top
    ax.set_theta_direction(-1)       #clockwise direction
    ax.set_rticks([])               #no radial ticks
    ax.set_thetagrids([])           # no angular grid
    ax.grid(False)
    ax.spines['polar'].set_visible(False)
    
    print(f"plotting circular mycelium forest...")
    print(f"  {len(angles)} trees arranged in 360° circle")
    print(f" debug max radius value: {max_radius:.2f}")
    print(f"  angular range per tree: {360/len(angles):.1f}°")

    fig.canvas.manager.set_window_title('mycelium_forest')#title it the package name
    plt.tight_layout()
    if auto_show:
        plt.show()
    
    return fig, ax, angles, all_trees_structure

def draw_circular_branches(ax, center_angle, center_radius, node_info, strength, 
                         level_params, current_depth=0, color_left_branch = "white", color_right_branch = "white"):
    """
    Recursively draw branches in circular coordinates
    """
    if node_info is None or current_depth >= len(level_params):
        return
    
    params = level_params[current_depth]
    
    # only draw if IG
    if node_info['information_gain'] > 0 and node_info['left_child'] and node_info['right_child']:
        
        #angular spread is based on normalized information gain
        normalized_ig = node_info.get('normalized_ig', 0)
        angular_spread = np.radians(normalized_ig * params['max_angle'])  # radians conversion
        
        #branch endpoints
        branch_radius = center_radius + params['branch_length']
        left_angle = center_angle - angular_spread
        right_angle = center_angle + angular_spread
        
        #alpha for given depth
        depth_alpha = strength * params['alpha_factor']
        
        #left branch
        ax.plot([center_angle, left_angle], [center_radius, branch_radius], 
               color=color_left_branch, alpha=depth_alpha, linewidth=params['line_width'])
        
        #right branch
        ax.plot([center_angle, right_angle], [center_radius, branch_radius], 
               color=color_right_branch, alpha=depth_alpha, linewidth=params['line_width'])
        
        #recursive bit
        if current_depth + 1 < len(level_params):
            draw_circular_branches(ax, left_angle, branch_radius, node_info['left_child'], 
                                 strength, level_params, current_depth + 1, color_left_branch = color_left_branch, color_right_branch = color_right_branch)
            draw_circular_branches(ax, right_angle, branch_radius, node_info['right_child'], 
                                 strength, level_params, current_depth + 1, color_left_branch = color_left_branch, color_right_branch = color_right_branch)

def run_tree_positioning_circular(correlations, forest_df, rf_model, forest_strength=None, 
                                max_branch_depth=25, resolution=300, **viz_params):
    """
    runs circular tree positioning visualization
    """
    tree_strengths = forest_df['tree_strength'].values
    
    positions, voting_spaces, tree_order = position_trees_2d(
        correlations, tree_strengths,
        grid_size=resolution, rmin=1.5, rmax=50, ring_width=1, gaussian_sigma=0.2
    )
    
    jittered_positions = add_jitter_to_positions(positions, jitter_strength=0.5)
    
    fig, ax, angles, tree_structures = visualize_tree_positions_circular(
        jittered_positions, tree_strengths, rf_model, 
        max_branch_depth=max_branch_depth,
        **viz_params
    )
    
    return jittered_positions, angles, tree_structures





#run script
if __name__ == "__main__":
    #demonstration
    analyzer, single_tree, forest_oob_strength, rf_model = demonstrate_single_tree_analysis()
    #analyzer = RFTreeAnalyzer(rf, X_train, y_train, X_test, y_test)
    #forest_oob_strength = rf.oob_score


    #summary stats
    forest = analyzer.get_tree_summary_stats()
    print(f"forest:{forest}")
    
    #tree corrs
    correlations = analyzer.calculate_tree_correlations()
    mean_correlation = np.mean(correlations[np.triu_indices_from(correlations, k=1)])
    print(f"\nmean tree correlation: {mean_correlation:.4f}")

    #viz
    arg = "both"
    
    # visualizing results
    if arg == "linear":
        #linear visualization
        jittered_positions, voting_spaces, tree_order, quality, tree_structures = run_tree_positioning(
            correlations, forest, forest_oob_strength, rf_model, max_branch_depth=25, resolution=300
        )
    elif arg == "circular":
        # circular visualization
        jittered_positions, angles, tree_structures = run_tree_positioning_circular(
            correlations, forest, rf_model, 
            forest_strength=forest_oob_strength, 
            max_branch_depth=25
        )
    elif arg == "barcode":
        #barcode visualization (=only inter-tree correlations)
        jittered_positions, voting_spaces, tree_order, quality, tree_structures = run_tree_positioning_barcode(
            correlations, forest, forest_oob_strength, resolution=300
        )
    else:
        print("hey, you can't do that\nyour options are 'barcode', 'linear' or 'circular'")



def mycelium_forest(rf_model, X_train, y_train, X_test=None, y_test=None, 
                   graph="linear", max_branch_depth=25, resolution=300,
                   trunk_height=0.15, base_branch_height=0.1, base_max_width=0.05,
                   trunk_length=0.2, base_branch_length=0.2, base_max_angle=45,
                   center_radius=0.2, base_branch_angle=45,color_trunk = "white",
                   color_left_branch = "white", color_right_branch = "white",
                   show_stats=True, return_data=False):
    """
    Visualize Random Forest trees with mycelium-inspired network representations.
    
    Parameters:
    -----------
    rf_model : RandomForestClassifier or RandomForestRegressor
        Trained Random Forest model
    X_train : array-like
        Training features
    y_train : array-like  
        Training targets
    X_test : array-like, optional
        Test features (if None, uses sample from training data)
    y_test : array-like, optional
        Test targets
    graph : str, default="linear"
        Visualization type: "linear", "circular", "barcode"
    max_branch_depth : int, default=25
        Maximum depth of tree structure to visualize
    resolution : int, default=300
        Grid resolution for tree positioning algorithm
    
    Linear Visualization Parameters:
    --------------------------------
    trunk_height : float, default=0.15
        Height of tree trunks
    base_branch_height : float, default=0.6
        Height of branch levels
    base_max_width : float, default=0.05
        Maximum branch width
    base_branch_angle : float, default=45
        Branch angle in degrees
    bottom_margin : float, default=0.1
        Margin below deepest branches
    
    Circular Visualization Parameters:
    ----------------------------------
    trunk_length : float, default=0.2
        Radial length of tree trunks
    base_branch_length : float, default=0.2
        Radial extension of branches
    base_max_angle : float, default=15
        Maximum angular spread of branches (degrees)
    center_radius : float, default=0.2
        Inner circle radius
    
    Other Parameters:
    -----------------
    show_stats : bool, default=True
        Print forest statistics
    return_data : bool, default=False
        Return analysis data along with visualizations
    
    Returns:
    --------
    dict : Analysis results and visualization objects (if return_data=True)
    """
    
    print("initiating MyceliumForest")
    
    #create analyzer
    analyzer = RFTreeAnalyzer(rf_model, X_train, y_train, X_test, y_test)
    
    # Get forest statistics
    forest_df = analyzer.get_tree_summary_stats()
    forest_oob_strength = rf_model.oob_score_ if hasattr(rf_model, 'oob_score_') else None
    
    # Calculate tree correlations
    correlations = analyzer.calculate_tree_correlations()
    mean_correlation = np.mean(correlations[np.triu_indices_from(correlations, k=1)])
    
    if show_stats:
        print(f"\n MyceliumForest overview:")
        print(f"   • number of trees: {rf_model.n_estimators}")
        print(f"   • mean tree correlation: {mean_correlation:.4f}")
        if forest_oob_strength:
            print(f"   • forest OOB strength: {forest_oob_strength:.4f}")
        print(f"   • mean tree strength: {forest_df['tree_strength'].mean():.4f}")
        print(f"   • tree depth range: {forest_df['tree_depth'].min():.0f}-{forest_df['tree_depth'].max():.0f}")
    
    # parameters
    linear_params = {
        'trunk_height': trunk_height,
        'base_branch_height': base_branch_height, 
        'base_max_width': base_max_width,
        'base_branch_angle': base_branch_angle,
        'color_trunk': color_trunk,
        'color_left_branch': color_left_branch,
        'color_right_branch': color_right_branch
    }
    
    circular_params = {
        'trunk_length': trunk_length,
        'base_branch_length': base_branch_length,
        'base_max_angle': base_max_angle,
        'center_radius': center_radius,
        'color_trunk': color_trunk,
        'color_left_branch': color_left_branch,
        'color_right_branch': color_right_branch
    }
    
    # viz based on graph type
    results = {}
    
    if graph.lower() == "linear":
        print("creating MyceliumForest visualization...")
        jittered_positions, voting_spaces, tree_order, quality, tree_structures = run_tree_positioning(
            correlations, forest_df, rf_model, forest_oob_strength, 
            max_branch_depth=max_branch_depth, resolution=resolution, **linear_params
        )
        results = {
            'positions': jittered_positions,
            'tree_structures': tree_structures,
            'quality': quality,
            'type': 'linear'
        }
        
    elif graph.lower() == "circular":
        print("creating circular MyceliumForest visualization...")
        jittered_positions, angles, tree_structures = run_tree_positioning_circular(
            correlations, forest_df, rf_model, forest_oob_strength, 
            max_branch_depth=max_branch_depth, resolution=resolution, **circular_params
        )
        results = {
            'positions': jittered_positions,
            'angles': angles,
            'tree_structures': tree_structures,
            'type': 'circular'
        }
        
    elif graph.lower() == "barcode":
        print("creating barcode visualization...")
        jittered_positions, voting_spaces, tree_order, quality, tree_structures = run_tree_positioning_barcode(
            correlations, forest_df, forest_oob_strength, resolution=resolution
        )
        results = {
            'positions': jittered_positions,
            'tree_structures': tree_structures,
            'quality': quality,
            'type': 'barcode'
        }      
    else:
        raise ValueError(f"unknown graph type: '{graph}'. use 'linear', 'circular' or 'barcode'")
    
    print("MyceliumForest complete")
    
    if return_data:
        return {
            'results': results,
            'analyzer': analyzer,
            'forest_stats': forest_df,
            'correlations': correlations,
            'mean_correlation': mean_correlation,
            'forest_strength': forest_oob_strength
        }
    else:
        return results

# alias
visualize_forest = mycelium_forest  # alternative name to call function

if __name__ == "__main__":
    # Simple demonstration
    analyzer, single_tree, forest_oob_strength, rf_model = demonstrate_single_tree_analysis()
    
    # Example usage of the package
    results = mycelium_forest(
        rf_model=rf_model, 
        X_train=analyzer.X_train, 
        y_train=analyzer.y_train,
        X_test=analyzer.X_test,
        y_test=analyzer.y_test,
        graph="linear",            #linear visualization
        max_branch_depth=25,        # max depth
        resolution=300,            #resolution (higher = more computationally expensive but also better for bigger forests)
        trunk_height=0.15,          #trunk sizes
        base_max_width=0.05,        # branch width
        show_stats=True,
        return_data=True
    )
    
    print(f"analysis completed | type: {results['results']['type']}")
    print("🍄thank you for using MyceliumForest🍄‍🟫")