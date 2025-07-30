import torch
import torch.nn as nn
import numpy as np
from .KANLayer import KANLayer
from .LBFGS import *
import os
import glob
from tqdm import tqdm
import random
import copy
import yaml
from .spline import curve2coef

class MultKAN(nn.Module):
    '''
    KAN class
    
    Attributes:
    -----------
        grid : int
            the number of grid intervals
        k : int
            spline order
        act_fun : a list of KANLayers
        depth : int
            depth of KAN
        width : list
            number of neurons in each layer.
            Without multiplication nodes, [2,5,5,3] means 2D inputs, 3D outputs, with 2 layers of 5 hidden neurons.
            With multiplication nodes, [2,[5,3],[5,1],3] means besides the [2,5,53] KAN, there are 3 (1) mul nodes in layer 1 (2). 
        mult_arity : int, or list of int lists
            multiplication arity for each multiplication node (the number of numbers to be multiplied)
        grid : int
            the number of grid intervals
        k : int
            the order of piecewise polynomial
        base_fun : fun
            residual function b(x). an activation function phi(x) = sb_scale * b(x) + sp_scale * spline(x)
        width_in : list
            The number of input neurons for each layer
        width_out : list
            The number of output neurons for each layer
        base_fun_name : str
            The base function b(x)
        grip_eps : float
            The parameter that interpolates between uniform grid and adaptive grid (based on sample quantile)
        node_bias : a list of 1D torch.float
        node_scale : a list of 1D torch.float
        subnode_bias : a list of 1D torch.float
        subnode_scale : a list of 1D torch.float
        affine_trainable : bool
            indicate whether affine parameters are trainable (node_bias, node_scale, subnode_bias, subnode_scale)
        sp_trainable : bool
            indicate whether the overall magnitude of splines is trainable
        sb_trainable : bool
            indicate whether the overall magnitude of base function is trainable
        node_scores : None or list of 1D torch.float
            node attribution score
        edge_scores : None or list of 2D torch.float
            edge attribution score
        subnode_scores : None or list of 1D torch.float
            subnode attribution score
        cache_data : None or 2D torch.float
            cached input data
        acts : None or a list of 2D torch.float
            activations on nodes
        state_id : int
            the state of the model (used to save checkpoint)
        round : int
            the number of times rewind() has been called
        device : str
    '''
    def __init__(self, width=None, grid=3, k=3, mult_arity = 2, noise_scale=0.3, scale_base_mu=0.0, scale_base_sigma=1.0, base_fun='silu', affine_trainable=False, grid_eps=0.02, grid_range=[-1, 1], sp_trainable=True, sb_trainable=True, seed=1, first_init=True, state_id=0, round=0, device='cpu'):
        '''
        initalize a KAN model
        
        Args:
        -----
            width : list of int
                Without multiplication nodes: :math:`[n_0, n_1, .., n_{L-1}]` specify the number of neurons in each layer (including inputs/outputs)
                With multiplication nodes: :math:`[[n_0,m_0=0], [n_1,m_1], .., [n_{L-1},m_{L-1}]]` specify the number of addition/multiplication nodes in each layer (including inputs/outputs)
            grid : int
                number of grid intervals. Default: 3.
            k : int
                order of piecewise polynomial. Default: 3.
            mult_arity : int, or list of int lists
                multiplication arity for each multiplication node (the number of numbers to be multiplied)
            noise_scale : float
                initial injected noise to spline.
            base_fun : str
                the residual function b(x). Default: 'silu'
            affine_trainable : bool
                affine parameters are updated or not. Affine parameters include node_scale, node_bias, subnode_scale, subnode_bias
            grid_eps : float
                When grid_eps = 1, the grid is uniform; when grid_eps = 0, the grid is partitioned using percentiles of samples. 0 < grid_eps < 1 interpolates between the two extremes.
            grid_range : list/np.array of shape (2,))
                setting the range of grids. Default: [-1,1]. This argument is not important if fit(update_grid=True) (by default updata_grid=True)
            sp_trainable : bool
                If true, scale_sp is trainable. Default: True.
            sb_trainable : bool
                If true, scale_base is trainable. Default: True.
            device : str
                device
            seed : int
                random seed
            state_id : int
                the state of the model (used to save checkpoint)
            round : int
                the number of times rewind() has been called
            device : str
            
        Returns:
        --------
            self
            
        Example
        -------
        >>> from kan import *
        >>> model = KAN(width=[2,5,1], grid=5, k=3, seed=0)
        checkpoint directory created: ./model
        saving model version 0.0
        '''
        super(MultKAN, self).__init__()

        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)

        ### initializeing the numerical front ###

        self.act_fun = []
        self.depth = len(width) - 1
        
        #print('haha1', width)
        for i in range(len(width)):
            #print(type(width[i]), type(width[i]) == int)
            if type(width[i]) == int or type(width[i]) == np.int64:
                width[i] = [width[i],0]
                
        #print('haha2', width)
            
        self.width = width
        
        # if mult_arity is just a scalar, we extend it to a list of lists
        # e.g, mult_arity = [[2,3],[4]] means that in the first hidden layer, 2 mult ops have arity 2 and 3, respectively;
        # in the second hidden layer, 1 mult op has arity 4.
        if isinstance(mult_arity, int):
            self.mult_homo = True # when homo is True, parallelization is possible
        else:
            self.mult_homo = False # when home if False, for loop is required. 
        self.mult_arity = mult_arity

        width_in = self.width_in
        width_out = self.width_out
        
        self.base_fun_name = base_fun
        if base_fun == 'silu':
            base_fun = torch.nn.SiLU()
        elif base_fun == 'identity':
            base_fun = torch.nn.Identity()
        elif base_fun == 'zero':
            base_fun = lambda x: x*0.
            
        self.grid_eps = grid_eps
        self.grid_range = grid_range
            
        
        for l in range(self.depth):
            # splines
            if isinstance(grid, list):
                grid_l = grid[l]
            else:
                grid_l = grid
                
            if isinstance(k, list):
                k_l = k[l]
            else:
                k_l = k
                    
            
            sp_batch = KANLayer(in_dim=width_in[l], out_dim=width_out[l+1], num=grid_l, k=k_l, noise_scale=noise_scale, scale_base_mu=scale_base_mu, scale_base_sigma=scale_base_sigma, scale_sp=1., base_fun=base_fun, grid_eps=grid_eps, grid_range=grid_range, sp_trainable=sp_trainable, sb_trainable=sb_trainable)
            self.act_fun.append(sp_batch)

        self.node_bias = []
        self.node_scale = []
        self.subnode_bias = []
        self.subnode_scale = []
        
        globals()['self.node_bias_0'] = torch.nn.Parameter(torch.zeros(3,1)).requires_grad_(False)
        exec('self.node_bias_0' + " = torch.nn.Parameter(torch.zeros(3,1)).requires_grad_(False)")
        
        for l in range(self.depth):
            exec(f'self.node_bias_{l} = torch.nn.Parameter(torch.zeros(width_in[l+1])).requires_grad_(affine_trainable)')
            exec(f'self.node_scale_{l} = torch.nn.Parameter(torch.ones(width_in[l+1])).requires_grad_(affine_trainable)')
            exec(f'self.subnode_bias_{l} = torch.nn.Parameter(torch.zeros(width_out[l+1])).requires_grad_(affine_trainable)')
            exec(f'self.subnode_scale_{l} = torch.nn.Parameter(torch.ones(width_out[l+1])).requires_grad_(affine_trainable)')
            exec(f'self.node_bias.append(self.node_bias_{l})')
            exec(f'self.node_scale.append(self.node_scale_{l})')
            exec(f'self.subnode_bias.append(self.subnode_bias_{l})')
            exec(f'self.subnode_scale.append(self.subnode_scale_{l})')
            
        
        self.act_fun = nn.ModuleList(self.act_fun)

        self.grid = grid
        self.k = k
        self.base_fun = base_fun

        self.affine_trainable = affine_trainable
        self.sp_trainable = sp_trainable
        self.sb_trainable = sb_trainable
            
        self.node_scores = None
        self.edge_scores = None
        self.subnode_scores = None
        
        self.cache_data = None
        self.acts = None
        
        self.state_id = 0
        self.round = round
        
        self.device = device
        self.to(device)
        

        self.input_id = torch.arange(self.width_in[0],)
        
    def to(self, device):
        '''
        move the model to device
        
        Args:
        -----
            device : str or device

        Returns:
        --------
            self
            
        Example
        -------
        >>> from kan import *
        >>> device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        >>> model = KAN(width=[2,5,1], grid=5, k=3, seed=0)
        >>> model.to(device)
        '''
        super(MultKAN, self).to(device)
        self.device = device
        
        for kanlayer in self.act_fun:
            kanlayer.to(device)
            
        return self
    
    @property
    def width_in(self):
        '''
        The number of input nodes for each layer
        '''
        width = self.width
        width_in = [width[l][0]+width[l][1] for l in range(len(width))]
        return width_in
        
    @property
    def width_out(self):
        '''
        The number of output subnodes for each layer
        '''
        width = self.width
        if self.mult_homo == True:
            width_out = [width[l][0]+self.mult_arity*width[l][1] for l in range(len(width))]
        else:
            width_out = [width[l][0]+int(np.sum(self.mult_arity[l])) for l in range(len(width))]
        return width_out
    
    @property
    def n_sum(self):
        '''
        The number of addition nodes for each layer
        '''
        width = self.width
        n_sum = [width[l][0] for l in range(1,len(width)-1)]
        return n_sum
    
    @property
    def n_mult(self):
        '''
        The number of multiplication nodes for each layer
        '''
        width = self.width
        n_mult = [width[l][1] for l in range(1,len(width)-1)]
        return n_mult
    
    @property
    def feature_score(self):
        '''
        attribution scores for inputs
        '''
        self.attribute()
        if self.node_scores == None:
            return None
        else:
            return self.node_scores[0]

    def initialize_from_another_model(self, another_model, x):
        '''
        initialize from another model of the same width, but their 'grid' parameter can be different. 
        Note this is equivalent to refine() when we don't want to keep another_model
        
        Args:
        -----
            another_model : MultKAN
            x : 2D torch.float

        Returns:
        --------
            self
            
        Example
        -------
        >>> from kan import *
        >>> model1 = KAN(width=[2,5,1], grid=3)
        >>> model2 = KAN(width=[2,5,1], grid=10)
        >>> x = torch.rand(100,2)
        >>> model2.initialize_from_another_model(model1, x)
        '''
        another_model(x)  # get activations
        batch = x.shape[0]

        self.initialize_grid_from_another_model(another_model, x)

        for l in range(self.depth):
            spb = self.act_fun[l]
            #spb_parent = another_model.act_fun[l]

            # spb = spb_parent
            preacts = another_model.spline_preacts[l]
            postsplines = another_model.spline_postsplines[l]
            self.act_fun[l].coef.data = curve2coef(preacts[:,0,:], postsplines.permute(0,2,1), spb.grid, k=spb.k)
            self.act_fun[l].scale_base.data = another_model.act_fun[l].scale_base.data
            self.act_fun[l].scale_sp.data = another_model.act_fun[l].scale_sp.data
            self.act_fun[l].mask.data = another_model.act_fun[l].mask.data

        for l in range(self.depth):
            self.node_bias[l].data = another_model.node_bias[l].data
            self.node_scale[l].data = another_model.node_scale[l].data
            
            self.subnode_bias[l].data = another_model.subnode_bias[l].data
            self.subnode_scale[l].data = another_model.subnode_scale[l].data

        return self.to(self.device)
    
    def saveckpt(self, path='model'):
        '''
        save the current model to files (configuration file and state file)

        Args:
        -----
            path : str
                the path where checkpoints are saved

        Returns:
        --------
            None

        Example
        -------
        >>> from kan import *
        >>> device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        >>> model = KAN(width=[2,5,1], grid=5, k=3, seed=0)
        >>> model.saveckpt('./mark')
        # There will be three files appearing in the current folder: mark_cache_data, mark_config.yml, mark_state
        '''
        model = self

        dic = dict(
            width = model.width,
            grid = model.grid,
            k = model.k,
            mult_arity = model.mult_arity,
            base_fun_name = model.base_fun_name,
            affine_trainable = model.affine_trainable,
            grid_eps = model.grid_eps,
            grid_range = model.grid_range,
            sp_trainable = model.sp_trainable,
            sb_trainable = model.sb_trainable,
            state_id = model.state_id,
            round = model.round,
            device = str(model.device)
        )

        if dic["device"].isdigit():
            dic["device"] = int(model.device)

        with open(f'{path}_config.yml', 'w') as outfile:
            yaml.dump(dic, outfile, default_flow_style=False)

        torch.save(model.state_dict(), f'{path}_state')
        torch.save(model.cache_data, f'{path}_cache_data')

    @staticmethod
    def loadckpt(path='model'):
        '''
        load checkpoint from path

        Args:
        -----
            path : str
                the path where checkpoints are saved

        Returns:
        --------
            MultKAN

        Example
        -------
        >>> from kan import *
        >>> model = KAN(width=[2,5,1], grid=5, k=3, seed=0)
        >>> model.saveckpt('./mark')
        >>> KAN.loadckpt('./mark')
        '''
        with open(f'{path}_config.yml', 'r') as stream:
            config = yaml.safe_load(stream)

        state = torch.load(f'{path}_state')

        model_load = MultKAN(width=config['width'],
                     grid=config['grid'],
                     k=config['k'],
                     mult_arity = config['mult_arity'],
                     base_fun=config['base_fun_name'],
                     affine_trainable=config['affine_trainable'],
                     grid_eps=config['grid_eps'],
                     grid_range=config['grid_range'],
                     sp_trainable=config['sp_trainable'],
                     sb_trainable=config['sb_trainable'],
                     state_id=config['state_id'],
                     first_init=False,
                     round = config['round']+1,
                     device = config['device'])

        model_load.load_state_dict(state)
        model_load.cache_data = torch.load(f'{path}_cache_data')
        return model_load

    def refine(self, new_grid):
        '''
        grid refinement
        
        Args:
        -----
            new_grid : init
                the number of grid intervals after refinement

        Returns:
        --------
            a refined model : MultKAN
            
        Example
        -------
        >>> from kan import *
        >>> device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        >>> model = KAN(width=[2,5,1], grid=5, k=3, seed=0)
        >>> print(model.grid)
        >>> x = torch.rand(100,2)
        >>> model.get_act(x)
        >>> model = model.refine(10)
        >>> print(model.grid)
        checkpoint directory created: ./model
        saving model version 0.0
        5
        saving model version 0.1
        10
        '''

        model_new = MultKAN(width=self.width, 
                     grid=new_grid, 
                     k=self.k, 
                     mult_arity=self.mult_arity, 
                     base_fun=self.base_fun_name, 
                     affine_trainable=self.affine_trainable, 
                     grid_eps=self.grid_eps, 
                     grid_range=self.grid_range, 
                     sp_trainable=self.sp_trainable,
                     sb_trainable=self.sb_trainable,
                     first_init=False,
                     state_id=self.state_id,
                     round=self.round,
                     device=self.device)
            
        model_new.initialize_from_another_model(self, self.cache_data)
        model_new.cache_data = self.cache_data
        model_new.grid = new_grid
        
        model_new.state_id += 1
        
        return model_new.to(self.device)
    

    def update_grid_from_samples(self, x):
        '''
        update grid from samples
        
        Args:
        -----
            x : 2D torch.tensor
                inputs

        Returns:
        --------
            None
            
        Example
        -------
        >>> from kan import *
        >>> model = KAN(width=[1,1], grid=5, k=3, seed=0)
        >>> print(model.act_fun[0].grid)
        >>> x = torch.linspace(-10,10,steps=101)[:,None]
        >>> model.update_grid_from_samples(x)
        >>> print(model.act_fun[0].grid)
        ''' 
        for l in range(self.depth):
            self.get_act(x)
            self.act_fun[l].update_grid_from_samples(self.acts[l])
            
    def update_grid(self, x):
        '''
        call update_grid_from_samples. This seems unnecessary but we retain it for the sake of classes that might inherit from MultKAN
        '''
        self.update_grid_from_samples(x)

    def initialize_grid_from_another_model(self, model, x):
        '''
        initialize grid from another model
        
        Args:
        -----
            model : MultKAN
                parent model
            x : 2D torch.tensor
                inputs

        Returns:
        --------
            None
            
        Example
        -------
        >>> from kan import *
        >>> model = KAN(width=[1,1], grid=5, k=3, seed=0)
        >>> print(model.act_fun[0].grid)
        >>> x = torch.linspace(-10,10,steps=101)[:,None]
        >>> model2 = KAN(width=[1,1], grid=10, k=3, seed=0)
        >>> model2.initialize_grid_from_another_model(model, x)
        >>> print(model2.act_fun[0].grid)
        '''
        model(x)
        for l in range(self.depth):
            self.act_fun[l].initialize_grid_from_parent(model.act_fun[l], model.acts[l])

    def forward(self, x):
        '''
        forward pass
        
        Args:
        -----
            x : 2D torch.tensor
                inputs
        Returns:
        --------
            None
            
        Example1
        --------
        >>> from kan import *
        >>> model = KAN(width=[2,5,1], grid=5, k=3, seed=0)
        >>> x = torch.rand(100,2)
        >>> model(x).shape
        '''
        x = x[:,self.input_id.long()]
        assert x.shape[1] == self.width_in[0]
        
        # cache data
        self.cache_data = x
        
        self.acts = []  # shape ([batch, n0], [batch, n1], ..., [batch, n_L])
        self.acts_premult = []
        self.spline_preacts = []
        self.spline_postsplines = []
        self.spline_postacts = []
        self.acts_scale = []
        self.acts_scale_spline = []
        self.subnode_actscale = []
        self.edge_actscale = []
        # self.neurons_scale = []

        self.acts.append(x)  # acts shape: (batch, width[l])

        for l in range(self.depth):
            
            x_numerical, preacts, postacts_numerical, postspline = self.act_fun[l](x)
            #print(preacts, postacts_numerical, postspline)
            


            x = x_numerical
            
            # subnode affine transform
            x = self.subnode_scale[l][None,:] * x + self.subnode_bias[l][None,:]
            

            # multiplication
            dim_sum = self.width[l+1][0]
            dim_mult = self.width[l+1][1]
            
            if self.mult_homo == True:
                for i in range(self.mult_arity-1):
                    if i == 0:
                        x_mult = x[:,dim_sum::self.mult_arity] * x[:,dim_sum+1::self.mult_arity]
                    else:
                        x_mult = x_mult * x[:,dim_sum+i+1::self.mult_arity]
                        
            else:
                for j in range(dim_mult):
                    acml_id = dim_sum + np.sum(self.mult_arity[l+1][:j])
                    for i in range(self.mult_arity[l+1][j]-1):
                        if i == 0:
                            x_mult_j = x[:,[acml_id]] * x[:,[acml_id+1]]
                        else:
                            x_mult_j = x_mult_j * x[:,[acml_id+i+1]]
                            
                    if j == 0:
                        x_mult = x_mult_j
                    else:
                        x_mult = torch.cat([x_mult, x_mult_j], dim=1)
                
            if self.width[l+1][1] > 0:
                x = torch.cat([x[:,:dim_sum], x_mult], dim=1)
            
            # x = x + self.biases[l].weight
            # node affine transform
            x = self.node_scale[l][None,:] * x + self.node_bias[l][None,:]
            
            self.acts.append(x.detach())
            
        
        return x

    def set_mode(self, l, i, j, mode, mask_n=None):
        if mode == "s":
            mask_n = 0.;
            mask_s = 1.
        elif mode == "n":
            mask_n = 1.;
            mask_s = 0.
        elif mode == "sn" or mode == "ns":
            if mask_n == None:
                mask_n = 1.
            else:
                mask_n = mask_n
            mask_s = 1.
        else:
            mask_n = 0.;
            mask_s = 0.

        self.act_fun[l].mask.data[i][j] = mask_n

    def get_range(self, l, i, j, verbose=True):
        '''
        Get the input range and output range of the (l,i,j) activation
        
        Args:
        -----
            l : int
                layer index
            i : int
                input neuron index
            j : int
                output neuron index
        
        Returns:
        --------
            x_min : float
                minimum of input
            x_max : float
                maximum of input
            y_min : float
                minimum of output
            y_max : float
                maximum of output
        
        Example
        -------
        >>> model = KAN(width=[2,3,1], grid=5, k=3, noise_scale=1.)
        >>> x = torch.normal(0,1,size=(100,2))
        >>> model(x) # do a forward pass to obtain model.acts
        >>> model.get_range(0,0,0)
        '''
        x = self.spline_preacts[l][:, j, i]
        y = self.spline_postacts[l][:, j, i]
        x_min = torch.min(x).cpu().detach().numpy()
        x_max = torch.max(x).cpu().detach().numpy()
        y_min = torch.min(y).cpu().detach().numpy()
        y_max = torch.max(y).cpu().detach().numpy()
        if verbose:
            print('x range: [' + '%.2f' % x_min, ',', '%.2f' % x_max, ']')
            print('y range: [' + '%.2f' % y_min, ',', '%.2f' % y_max, ']')
        return x_min, x_max, y_min, y_max

    def reg(self, reg_metric, lamb_l1, lamb_entropy, lamb_coef, lamb_coefdiff):
        '''
        Get regularization
        
        Args:
        -----
            reg_metric : the regularization metric
                'edge_forward_spline_n', 'edge_forward_spline_u', 'edge_forward_sum', 'edge_backward', 'node_backward'
            lamb_l1 : float
                l1 penalty strength
            lamb_entropy : float
                entropy penalty strength
            lamb_coef : float
                coefficient penalty strength
            lamb_coefdiff : float
                coefficient smoothness strength
        
        Returns:
        --------
            reg_ : torch.float
        
        Example
        -------
        >>> model = KAN(width=[2,3,1], grid=5, k=3, noise_scale=1.)
        >>> x = torch.rand(100,2)
        >>> model.get_act(x)
        >>> model.reg('edge_forward_spline_n', 1.0, 2.0, 1.0, 1.0)
        '''
        if reg_metric == 'edge_forward_spline_n':
            acts_scale = self.acts_scale_spline
            
        elif reg_metric == 'edge_forward_sum':
            acts_scale = self.acts_scale
            
        elif reg_metric == 'edge_forward_spline_u':
            acts_scale = self.edge_actscale
            
        elif reg_metric == 'edge_backward':
            acts_scale = self.edge_scores
            
        elif reg_metric == 'node_backward':
            acts_scale = self.node_attribute_scores
            
        else:
            raise Exception(f'reg_metric = {reg_metric} not recognized!')
        
        reg_ = 0.
        for i in range(len(acts_scale)):
            vec = acts_scale[i]

            l1 = torch.sum(vec)
            p_row = vec / (torch.sum(vec, dim=1, keepdim=True) + 1)
            p_col = vec / (torch.sum(vec, dim=0, keepdim=True) + 1)
            entropy_row = - torch.mean(torch.sum(p_row * torch.log2(p_row + 1e-4), dim=1))
            entropy_col = - torch.mean(torch.sum(p_col * torch.log2(p_col + 1e-4), dim=0))
            reg_ += lamb_l1 * l1 + lamb_entropy * (entropy_row + entropy_col)  # both l1 and entropy

        # regularize coefficient to encourage spline to be zero
        for i in range(len(self.act_fun)):
            coeff_l1 = torch.sum(torch.mean(torch.abs(self.act_fun[i].coef), dim=1))
            coeff_diff_l1 = torch.sum(torch.mean(torch.abs(torch.diff(self.act_fun[i].coef)), dim=1))
            reg_ += lamb_coef * coeff_l1 + lamb_coefdiff * coeff_diff_l1

        return reg_
    
    def get_reg(self, reg_metric, lamb_l1, lamb_entropy, lamb_coef, lamb_coefdiff):
        '''
        Get regularization. This seems unnecessary but in case a class wants to inherit this, it may want to rewrite get_reg, but not reg.
        '''
        return self.reg(reg_metric, lamb_l1, lamb_entropy, lamb_coef, lamb_coefdiff)
    

    def get_params(self):
        '''
        Get parameters
        '''
        return self.parameters()
        
            
    def fit(self, dataset, opt="LBFGS", steps=100, log=1, lamb=0., lamb_l1=1., lamb_entropy=2., lamb_coef=0., lamb_coefdiff=0., update_grid=True, grid_update_num=10, loss_fn=None, lr=1.,start_grid_update_step=-1, stop_grid_update_step=50, batch=-1,
              metrics=None, in_vars=None, out_vars=None, beta=3, reg_metric='edge_forward_spline_n', display_metrics=None):
        '''
        training

        Args:
        -----
            dataset : dic
                contains dataset['train_input'], dataset['train_label'], dataset['test_input'], dataset['test_label']
            opt : str
                "LBFGS" or "Adam"
            steps : int
                training steps
            log : int
                logging frequency
            lamb : float
                overall penalty strength
            lamb_l1 : float
                l1 penalty strength
            lamb_entropy : float
                entropy penalty strength
            lamb_coef : float
                coefficient magnitude penalty strength
            lamb_coefdiff : float
                difference of nearby coefficits (smoothness) penalty strength
            update_grid : bool
                If True, update grid regularly before stop_grid_update_step
            grid_update_num : int
                the number of grid updates before stop_grid_update_step
            start_grid_update_step : int
                no grid updates before this training step
            stop_grid_update_step : int
                no grid updates after this training step
            loss_fn : function
                loss function
            lr : float
                learning rate
            batch : int
                batch size, if -1 then full.
            reg_metric : str
                regularization metric. Choose from {'edge_forward_spline_n', 'edge_forward_spline_u', 'edge_forward_sum', 'edge_backward', 'node_backward'}
            metrics : a list of metrics (as functions)
                the metrics to be computed in training
            display_metrics : a list of functions
                the metric to be displayed in tqdm progress bar

        Returns:
        --------
            results : dic
                results['train_loss'], 1D array of training losses (RMSE)
                results['test_loss'], 1D array of test losses (RMSE)
                results['reg'], 1D array of regularization
                other metrics specified in metrics

        Example
        -------
        >>> from kan import *
        >>> model = KAN(width=[2,5,1], grid=5, k=3, noise_scale=0.3, seed=2)
        >>> f = lambda x: torch.exp(torch.sin(torch.pi*x[:,[0]]) + x[:,[1]]**2)
        >>> dataset = create_dataset(f, n_var=2)
        >>> model.fit(dataset, opt='LBFGS', steps=20, lamb=0.001);
        >>> model.plot()
        # Most examples in toturals involve the fit() method. Please check them for useness.
        '''


        pbar = tqdm(range(steps), desc='description', ncols=100)

        if loss_fn == None:
            loss_fn = loss_fn_eval = lambda x, y: torch.mean((x - y) ** 2)
        else:
            loss_fn = loss_fn_eval = loss_fn

        grid_update_freq = int(stop_grid_update_step / grid_update_num)

        if opt == "Adam":
            optimizer = torch.optim.Adam(self.get_params(), lr=lr)
        elif opt == "LBFGS":
            optimizer = LBFGS(self.get_params(), lr=lr, history_size=10, line_search_fn="strong_wolfe", tolerance_grad=1e-32, tolerance_change=1e-32, tolerance_ys=1e-32)

        results = {}
        results['train_loss'] = []
        results['test_loss'] = []
        results['reg'] = []
        if metrics != None:
            for i in range(len(metrics)):
                results[metrics[i].__name__] = []

        if batch == -1 or batch > dataset['train_input'].shape[0]:
            batch_size = dataset['train_input'].shape[0]
            batch_size_test = dataset['test_input'].shape[0]
        else:
            batch_size = batch
            batch_size_test = batch

        global train_loss, reg_

        def closure():
            global train_loss, reg_
            optimizer.zero_grad()
            pred = self.forward(dataset['train_input'][train_id])
            train_loss = loss_fn(pred, dataset['train_label'][train_id])
            reg_ = torch.tensor(0.)
            objective = train_loss + lamb * reg_
            objective.backward()
            return objective

        for _ in pbar:
            
            train_id = np.random.choice(dataset['train_input'].shape[0], batch_size, replace=False)
            test_id = np.random.choice(dataset['test_input'].shape[0], batch_size_test, replace=False)

            if _ % grid_update_freq == 0 and _ < stop_grid_update_step and update_grid and _ >= start_grid_update_step:
                self.update_grid(dataset['train_input'][train_id])

            if opt == "LBFGS":
                optimizer.step(closure)

            if opt == "Adam":
                pred = self.forward(dataset['train_input'][train_id])
                train_loss = loss_fn(pred, dataset['train_label'][train_id])
                reg_ = torch.tensor(0.)
                loss = train_loss + lamb * reg_
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            test_loss = loss_fn_eval(self.forward(dataset['test_input'][test_id]), dataset['test_label'][test_id])
            
            
            if metrics != None:
                for i in range(len(metrics)):
                    results[metrics[i].__name__].append(metrics[i]().item())

            results['train_loss'].append(torch.sqrt(train_loss).cpu().detach().numpy())
            results['test_loss'].append(torch.sqrt(test_loss).cpu().detach().numpy())
            results['reg'].append(reg_.cpu().detach().numpy())

            if _ % log == 0:
                if display_metrics == None:
                    pbar.set_description("| train_loss: %.2e | test_loss: %.2e | reg: %.2e | " % (torch.sqrt(train_loss).cpu().detach().numpy(), torch.sqrt(test_loss).cpu().detach().numpy(), reg_.cpu().detach().numpy()))
                else:
                    string = ''
                    data = ()
                    for metric in display_metrics:
                        string += f' {metric}: %.2e |'
                        try:
                            results[metric]
                        except:
                            raise Exception(f'{metric} not recognized')
                        data += (results[metric][-1],)
                    pbar.set_description(string % data)
        return results

    def prune_node(self, threshold=1e-2, mode="auto", active_neurons_id=None, log_history=True):
        '''
        pruning nodes

        Args:
        -----
            threshold : float
                if the attribution score of a neuron is below the threshold, it is considered dead and will be removed
            mode : str
                'auto' or 'manual'. with 'auto', nodes are automatically pruned using threshold. with 'manual', active_neurons_id should be passed in.
            
        Returns:
        --------
            pruned network : MultKAN

        Example
        -------
        >>> from kan import *
        >>> model = KAN(width=[2,5,1], grid=5, k=3, noise_scale=0.3, seed=2)
        >>> f = lambda x: torch.exp(torch.sin(torch.pi*x[:,[0]]) + x[:,[1]]**2)
        >>> dataset = create_dataset(f, n_var=2)
        >>> model.fit(dataset, opt='LBFGS', steps=20, lamb=0.001);
        >>> model = model.prune_node()
        >>> model.plot()
        '''
        if self.acts == None:
            self.get_act()
        
        mask_up = [torch.ones(self.width_in[0], device=self.device)]
        mask_down = []
        active_neurons_up = [list(range(self.width_in[0]))]
        active_neurons_down = []
        num_sums = []
        num_mults = []
        mult_arities = [[]]
        
        if active_neurons_id != None:
            mode = "manual"

        for i in range(len(self.acts_scale) - 1):
            
            mult_arity = []
            
            if mode == "auto":
                self.attribute()
                overall_important_up = self.node_scores[i+1] > threshold
                
            elif mode == "manual":
                overall_important_up = torch.zeros(self.width_in[i + 1], dtype=torch.bool, device=self.device)
                overall_important_up[active_neurons_id[i]] = True
                
                
            num_sum = torch.sum(overall_important_up[:self.width[i+1][0]])
            num_mult = torch.sum(overall_important_up[self.width[i+1][0]:])
            if self.mult_homo == True:
                overall_important_down = torch.cat([overall_important_up[:self.width[i+1][0]], (overall_important_up[self.width[i+1][0]:][None,:].expand(self.mult_arity,-1)).T.reshape(-1,)], dim=0)
            else:
                overall_important_down = overall_important_up[:self.width[i+1][0]]
                for j in range(overall_important_up[self.width[i+1][0]:].shape[0]):
                    active_bool = overall_important_up[self.width[i+1][0]+j]
                    arity = self.mult_arity[i+1][j]
                    overall_important_down = torch.cat([overall_important_down, torch.tensor([active_bool]*arity).to(self.device)])
                    if active_bool:
                        mult_arity.append(arity)
            
            num_sums.append(num_sum.item())
            num_mults.append(num_mult.item())

            mask_up.append(overall_important_up.float())
            mask_down.append(overall_important_down.float())

            active_neurons_up.append(torch.where(overall_important_up == True)[0])
            active_neurons_down.append(torch.where(overall_important_down == True)[0])
            
            mult_arities.append(mult_arity)

        active_neurons_down.append(list(range(self.width_out[-1])))
        mask_down.append(torch.ones(self.width_out[-1], device=self.device))
        
        if self.mult_homo == False:
            mult_arities.append(self.mult_arity[-1])

        self.mask_up = mask_up
        self.mask_down = mask_down

        # update act_fun[l].mask up
        for l in range(len(self.acts_scale) - 1):
            for i in range(self.width_in[l + 1]):
                if i not in active_neurons_up[l + 1]:
                    self.remove_node(l + 1, i, mode='up',log_history=False)
                    
            for i in range(self.width_out[l + 1]):
                if i not in active_neurons_down[l]:
                    self.remove_node(l + 1, i, mode='down',log_history=False)

        model2 = MultKAN(copy.deepcopy(self.width), grid=self.grid, k=self.k, base_fun=self.base_fun_name, mult_arity=self.mult_arity, first_init=False, state_id=self.state_id, round=self.round).to(self.device)
        model2.load_state_dict(self.state_dict())
        
        width_new = [self.width[0]]
        
        for i in range(len(self.acts_scale)):
            
            if i < len(self.acts_scale) - 1:
                num_sum = num_sums[i]
                num_mult = num_mults[i]
                model2.node_bias[i].data = model2.node_bias[i].data[active_neurons_up[i+1]]
                model2.node_scale[i].data = model2.node_scale[i].data[active_neurons_up[i+1]]
                model2.subnode_bias[i].data = model2.subnode_bias[i].data[active_neurons_down[i]]
                model2.subnode_scale[i].data = model2.subnode_scale[i].data[active_neurons_down[i]]
                model2.width[i+1] = [num_sum, num_mult]
                
                model2.act_fun[i].out_dim_sum = num_sum
                model2.act_fun[i].out_dim_mult = num_mult
                
                width_new.append([num_sum, num_mult])

            model2.act_fun[i] = model2.act_fun[i].get_subset(active_neurons_up[i], active_neurons_down[i])
            
        model2.cache_data = self.cache_data
        model2.acts = None
        
        width_new.append(self.width[-1])
        model2.width = width_new
        
        if self.mult_homo == False:
            model2.mult_arity = mult_arities
        
        if log_history:
            model2.state_id += 1
        
        return model2
    
    def prune_edge(self, threshold=3e-2, log_history=True):
        '''
        pruning edges

        Args:
        -----
            threshold : float
                if the attribution score of an edge is below the threshold, it is considered dead and will be set to zero.
            
        Returns:
        --------
            pruned network : MultKAN

        Example
        -------
        >>> from kan import *
        >>> model = KAN(width=[2,5,1], grid=5, k=3, noise_scale=0.3, seed=2)
        >>> f = lambda x: torch.exp(torch.sin(torch.pi*x[:,[0]]) + x[:,[1]]**2)
        >>> dataset = create_dataset(f, n_var=2)
        >>> model.fit(dataset, opt='LBFGS', steps=20, lamb=0.001);
        >>> model = model.prune_edge()
        >>> model.plot()
        '''
        if self.acts == None:
            self.get_act()
        
        for i in range(len(self.width)-1):
            #self.act_fun[i].mask.data = ((self.acts_scale[i] > threshold).permute(1,0)).float()
            old_mask = self.act_fun[i].mask.data
            self.act_fun[i].mask.data = ((self.edge_scores[i] > threshold).permute(1,0)*old_mask).float()
    
    def prune(self, node_th=1e-2, edge_th=3e-2):
        '''
        prune (both nodes and edges)

        Args:
        -----
            node_th : float
                if the attribution score of a node is below node_th, it is considered dead and will be set to zero.
            edge_th : float
                if the attribution score of an edge is below node_th, it is considered dead and will be set to zero.
            
        Returns:
        --------
            pruned network : MultKAN

        Example
        -------
        >>> from kan import *
        >>> model = KAN(width=[2,5,1], grid=5, k=3, noise_scale=0.3, seed=2)
        >>> f = lambda x: torch.exp(torch.sin(torch.pi*x[:,[0]]) + x[:,[1]]**2)
        >>> dataset = create_dataset(f, n_var=2)
        >>> model.fit(dataset, opt='LBFGS', steps=20, lamb=0.001);
        >>> model = model.prune()
        >>> model.plot()
        '''
        if self.acts == None:
            self.get_act()
        
        self = self.prune_node(node_th, log_history=False)
        #self.prune_node(node_th, log_history=False)
        self.forward(self.cache_data)
        self.attribute()
        self.prune_edge(edge_th, log_history=False)
        return self
    
    def prune_input(self, threshold=1e-2, active_inputs=None, log_history=True):
        '''
        prune inputs

        Args:
        -----
            threshold : float
                if the attribution score of the input feature is below threshold, it is considered irrelevant.
            active_inputs : None or list
                if a list is passed, the manual mode will disregard attribution score and prune as instructed.
            
        Returns:
        --------
            pruned network : MultKAN

        Example1
        --------
        >>> # automatic
        >>> from kan import *
        >>> model = KAN(width=[3,5,1], grid=5, k=3, noise_scale=0.3, seed=2)
        >>> f = lambda x: 1 * x[:,[0]]**2 + 0.3 * x[:,[1]]**2 + 0.0 * x[:,[2]]**2
        >>> dataset = create_dataset(f, n_var=3)
        >>> model.fit(dataset, opt='LBFGS', steps=20, lamb=0.001);
        >>> model.plot()
        >>> model = model.prune_input()
        >>> model.plot()
        
        Example2
        --------
        >>> # automatic
        >>> from kan import *
        >>> model = KAN(width=[3,5,1], grid=5, k=3, noise_scale=0.3, seed=2)
        >>> f = lambda x: 1 * x[:,[0]]**2 + 0.3 * x[:,[1]]**2 + 0.0 * x[:,[2]]**2
        >>> dataset = create_dataset(f, n_var=3)
        >>> model.fit(dataset, opt='LBFGS', steps=20, lamb=0.001);
        >>> model.plot()
        >>> model = model.prune_input(active_inputs=[0,1])
        >>> model.plot()
        '''
        if active_inputs == None:
            self.attribute()
            input_score = self.node_scores[0]
            input_mask = input_score > threshold
            print('keep:', input_mask.tolist())
            input_id = torch.where(input_mask==True)[0]
            
        else:
            input_id = torch.tensor(active_inputs, dtype=torch.long).to(self.device)
        
        model2 = MultKAN(copy.deepcopy(self.width), grid=self.grid, k=self.k, base_fun=self.base_fun, mult_arity=self.mult_arity, first_init=False, state_id=self.state_id, round=self.round).to(self.device)
        model2.load_state_dict(self.state_dict())

        model2.act_fun[0] = model2.act_fun[0].get_subset(input_id, torch.arange(self.width_out[1]))

        model2.cache_data = self.cache_data
        model2.acts = None

        model2.width[0] = [len(input_id), 0]
        model2.input_id = input_id
        
        if log_history:
            self.log_history('prune_input')
            model2.state_id += 1
        
        return model2

    def remove_edge(self, l, i, j, log_history=True):
        '''
        remove activtion phi(l,i,j) (set its mask to zero)
        '''
        self.act_fun[l].mask[i][j] = 0.
        if log_history:
            self.log_history('remove_edge')

    def remove_node(self, l ,i, mode='all', log_history=True):
        '''
        remove neuron (l,i) (set the masks of all incoming and outgoing activation functions to zero)
        '''
        if mode == 'down':
            self.act_fun[l - 1].mask[:, i] = 0.

        elif mode == 'up':
            self.act_fun[l].mask[i, :] = 0.
            
        else:
            self.remove_node(l, i, mode='up')
            self.remove_node(l, i, mode='down')
            
        if log_history:
            self.log_history('remove_node')
            
            
    def attribute(self, l=None, i=None, out_score=None, plot=True):
        '''
        get attribution scores

        Args:
        -----
            l : None or int
                layer index
            i : None or int
                neuron index
            out_score : None or 1D torch.float
                specify output scores
            plot : bool
                when plot = True, display the bar show
            
        Returns:
        --------
            attribution scores

        Example
        -------
        >>> from kan import *
        >>> model = KAN(width=[3,5,1], grid=5, k=3, noise_scale=0.3, seed=2)
        >>> f = lambda x: 1 * x[:,[0]]**2 + 0.3 * x[:,[1]]**2 + 0.0 * x[:,[2]]**2
        >>> dataset = create_dataset(f, n_var=3)
        >>> model.fit(dataset, opt='LBFGS', steps=20, lamb=0.001);
        >>> model.attribute()
        >>> model.feature_score
        '''
        # output (out_dim, in_dim)
        
        if l != None:
            self.attribute()
            out_score = self.node_scores[l]
       
        if self.acts == None:
            self.get_act()

        def score_node2subnode(node_score, width, mult_arity, out_dim):

            assert np.sum(width) == node_score.shape[1]
            if isinstance(mult_arity, int):
                n_subnode = width[0] + mult_arity * width[1]
            else:
                n_subnode = width[0] + int(np.sum(mult_arity))

            #subnode_score_leaf = torch.zeros(out_dim, n_subnode).requires_grad_(True)
            #subnode_score = subnode_score_leaf.clone()
            #subnode_score[:,:width[0]] = node_score[:,:width[0]]
            subnode_score = node_score[:,:width[0]]
            if isinstance(mult_arity, int):
                #subnode_score[:,width[0]:] = node_score[:,width[0]:][:,:,None].expand(out_dim, node_score[width[0]:].shape[0], mult_arity).reshape(out_dim,-1)
                subnode_score = torch.cat([subnode_score, node_score[:,width[0]:][:,:,None].expand(out_dim, node_score[:,width[0]:].shape[1], mult_arity).reshape(out_dim,-1)], dim=1)
            else:
                acml = width[0]
                for i in range(len(mult_arity)):
                    #subnode_score[:, acml:acml+mult_arity[i]] = node_score[:, width[0]+i]
                    subnode_score = torch.cat([subnode_score, node_score[:, width[0]+i].expand(out_dim, mult_arity[i])], dim=1)
                    acml += mult_arity[i]
            return subnode_score


        node_scores = []
        subnode_scores = []
        edge_scores = []
        
        l_query = l
        if l == None:
            l_end = self.depth
        else:
            l_end = l

        # back propagate from the queried layer
        out_dim = self.width_in[l_end]
        if out_score == None:
            node_score = torch.eye(out_dim).requires_grad_(True)
        else:
            node_score = torch.diag(out_score).requires_grad_(True)
        node_scores.append(node_score)
        
        device = self.act_fun[0].grid.device

        for l in range(l_end,0,-1):

            # node to subnode 
            if isinstance(self.mult_arity, int):
                subnode_score = score_node2subnode(node_score, self.width[l], self.mult_arity, out_dim=out_dim)
            else:
                mult_arity = self.mult_arity[l]
                #subnode_score = score_node2subnode(node_score, self.width[l], mult_arity)
                subnode_score = score_node2subnode(node_score, self.width[l], mult_arity, out_dim=out_dim)

            subnode_scores.append(subnode_score)
            # subnode to edge
            #print(self.edge_actscale[l-1].device, subnode_score.device, self.subnode_actscale[l-1].device)
            edge_score = torch.einsum('ij,ki,i->kij', self.edge_actscale[l-1], subnode_score.to(device), 1/(self.subnode_actscale[l-1]+1e-4))
            edge_scores.append(edge_score)

            # edge to node
            node_score = torch.sum(edge_score, dim=1)
            node_scores.append(node_score)

        self.node_scores_all = list(reversed(node_scores))
        self.edge_scores_all = list(reversed(edge_scores))
        self.subnode_scores_all = list(reversed(subnode_scores))

        self.node_scores = [torch.mean(l, dim=0) for l in self.node_scores_all]
        self.edge_scores = [torch.mean(l, dim=0) for l in self.edge_scores_all]
        self.subnode_scores = [torch.mean(l, dim=0) for l in self.subnode_scores_all]

        # return
        if l_query != None:
            if i == None:
                return self.node_scores_all[0]
            else:
                return self.node_scores_all[0][i]
            
    def node_attribute(self):
        self.node_attribute_scores = []
        for l in range(1, self.depth+1):
            node_attr = self.attribute(l)
            self.node_attribute_scores.append(node_attr)
            
    def feature_interaction(self, l, neuron_th = 1e-2, feature_th = 1e-2):
        '''
        get feature interaction

        Args:
        -----
            l : int
                layer index
            neuron_th : float
                threshold to determine whether a neuron is active
            feature_th : float
                threshold to determine whether a feature is active
            
        Returns:
        --------
            dictionary

        Example
        -------
        >>> from kan import *
        >>> model = KAN(width=[3,5,1], grid=5, k=3, noise_scale=0.3, seed=2)
        >>> f = lambda x: 1 * x[:,[0]]**2 + 0.3 * x[:,[1]]**2 + 0.0 * x[:,[2]]**2
        >>> dataset = create_dataset(f, n_var=3)
        >>> model.fit(dataset, opt='LBFGS', steps=20, lamb=0.001);
        >>> model.attribute()
        >>> model.feature_interaction(1)
        '''
        dic = {}
        width = self.width_in[l]

        for i in range(width):
            score = self.attribute(l,i,plot=False)

            if torch.max(score) > neuron_th:
                features = tuple(torch.where(score > torch.max(score) * feature_th)[0].detach().numpy())
                if features in dic.keys():
                    dic[features] += 1
                else:
                    dic[features] = 1

        return dic

    def expand_depth(self):
        '''
        expand network depth, add an indentity layer to the end. For usage, please refer to tutorials interp_3_KAN_compiler.ipynb.
        
        Args:
        -----
            var : None or a list of sympy expression
                input variables
            normalizer : [mean, std]
            output_normalizer : [mean, std]
            
        Returns:
        --------
            None
        '''
        self.depth += 1

        # add kanlayer, set mask to zero
        dim_out = self.width_in[-1]
        layer = KANLayer(dim_out, dim_out, num=self.grid, k=self.k)
        layer.mask *= 0.
        self.act_fun.append(layer)

        self.width.append([dim_out, 0])
        self.mult_arity.append([])

        self.node_bias.append(torch.nn.Parameter(torch.zeros(dim_out,device=self.device)).requires_grad_(self.affine_trainable))
        self.node_scale.append(torch.nn.Parameter(torch.ones(dim_out,device=self.device)).requires_grad_(self.affine_trainable))
        self.subnode_bias.append(torch.nn.Parameter(torch.zeros(dim_out,device=self.device)).requires_grad_(self.affine_trainable))
        self.subnode_scale.append(torch.nn.Parameter(torch.ones(dim_out,device=self.device)).requires_grad_(self.affine_trainable))

    def expand_width(self, layer_id, n_added_nodes, sum_bool=True, mult_arity=2):
        '''
        expand network width. For usage, please refer to tutorials interp_3_KAN_compiler.ipynb.

        Args:
        -----
            layer_id : int
                layer index
            n_added_nodes : init
                the number of added nodes
            sum_bool : bool
                if sum_bool == True, added nodes are addition nodes; otherwise multiplication nodes
            mult_arity : init
                multiplication arity (the number of numbers to be multiplied)

        Returns:
        --------
            None
        '''
        def _expand(l, n_added_nodes, sum_bool=True, mult_arity=2, added_dim='out'):
            # This helper function expands a single layer's input or output dimension.

            old_kan_layer = self.act_fun[l]
            in_dim = old_kan_layer.in_dim
            out_dim = old_kan_layer.out_dim

            # Determine the number of new subnodes to add (for multiplication nodes)
            if not sum_bool:
                if isinstance(mult_arity, int):
                    mult_arity_list = [mult_arity] * n_added_nodes
                else:
                    mult_arity_list = mult_arity
                n_added_subnodes = int(np.sum(mult_arity_list))
            else:
                n_added_subnodes = n_added_nodes

            # --- Case 1: Expanding the output dimension of the layer ---
            if added_dim == 'out':
                new_out_dim = out_dim + n_added_subnodes
                # Create a new, larger KANLayer
                new_kan_layer = KANLayer(in_dim, new_out_dim, num=self.grid, k=self.k, base_fun=self.base_fun)

                if sum_bool:
                    # New sum nodes are added at the beginning of the output dimension
                    # Copy old parameters to the end of the new tensors
                    new_kan_layer.coef.data[:, :, n_added_nodes:] = old_kan_layer.coef.data
                    new_kan_layer.scale_base.data[:, n_added_nodes:] = old_kan_layer.scale_base.data
                    new_kan_layer.scale_sp.data[:, n_added_nodes:] = old_kan_layer.scale_sp.data
                    new_kan_layer.mask.data[:, n_added_nodes:] = old_kan_layer.mask.data

                    # Expand affine parameters by prepending new ones
                    self.node_scale[l].data = torch.nn.Parameter(torch.cat([torch.ones(n_added_nodes, device=self.device), self.node_scale[l].data]))
                    self.node_bias[l].data = torch.nn.Parameter(torch.cat([torch.zeros(n_added_nodes, device=self.device), self.node_bias[l].data]))
                    self.subnode_scale[l].data = torch.nn.Parameter(torch.cat([torch.ones(n_added_subnodes, device=self.device), self.subnode_scale[l].data]))
                    self.subnode_bias[l].data = torch.nn.Parameter(torch.cat([torch.zeros(n_added_subnodes, device=self.device), self.subnode_bias[l].data]))
                else: # Multiplication nodes
                    # New multiplication nodes are added at the end
                    # Copy old parameters to the beginning of the new tensors
                    new_kan_layer.coef.data[:, :, :out_dim] = old_kan_layer.coef.data
                    new_kan_layer.scale_base.data[:, :out_dim] = old_kan_layer.scale_base.data
                    new_kan_layer.scale_sp.data[:, :out_dim] = old_kan_layer.scale_sp.data
                    new_kan_layer.mask.data[:, :out_dim] = old_kan_layer.mask.data

                    # Expand affine parameters by appending new ones
                    self.node_scale[l].data = torch.nn.Parameter(torch.cat([self.node_scale[l].data, torch.ones(n_added_nodes, device=self.device)]))
                    self.node_bias[l].data = torch.nn.Parameter(torch.cat([self.node_bias[l].data, torch.zeros(n_added_nodes, device=self.device)]))
                    self.subnode_scale[l].data = torch.nn.Parameter(torch.cat([self.subnode_scale[l].data, torch.ones(n_added_subnodes, device=self.device)]))
                    self.subnode_bias[l].data = torch.nn.Parameter(torch.cat([self.subnode_bias[l].data, torch.zeros(n_added_subnodes, device=self.device)]))

                # Replace the old layer with the new expanded one
                self.act_fun[l] = new_kan_layer

            # --- Case 2: Expanding the input dimension of the layer ---
            elif added_dim == 'in':
                new_in_dim = in_dim + n_added_nodes
                # Create a new, larger KANLayer
                new_kan_layer = KANLayer(new_in_dim, out_dim, num=self.grid, k=self.k, base_fun=self.base_fun)

                # New nodes are added at the beginning of the input dimension
                # Copy old parameters to the end of the new tensors
                new_kan_layer.grid.data[n_added_nodes:, :] = old_kan_layer.grid.data
                new_kan_layer.coef.data[n_added_nodes:, :, :] = old_kan_layer.coef.data
                new_kan_layer.scale_base.data[n_added_nodes:, :] = old_kan_layer.scale_base.data
                new_kan_layer.scale_sp.data[n_added_nodes:, :] = old_kan_layer.scale_sp.data
                new_kan_layer.mask.data[n_added_nodes:, :] = old_kan_layer.mask.data

                # Replace the old layer with the new expanded one
                self.act_fun[l] = new_kan_layer

        # --- Main logic of expand_width ---

        # Expand the output of the previous layer
        _expand(layer_id - 1, n_added_nodes, sum_bool, mult_arity, added_dim='out')
        # Expand the input of the current layer
        _expand(layer_id, n_added_nodes, sum_bool, mult_arity, added_dim='in')

        # Update the network width definition
        if sum_bool:
            self.width[layer_id][0] += n_added_nodes
        else:
            if isinstance(mult_arity, int):
                mult_arity = [mult_arity] * n_added_nodes
            self.width[layer_id][1] += n_added_nodes
            self.mult_arity[layer_id] += mult_arity
    def module(self, start_layer, chain):
        '''
        specify network modules
        
        Args:
        -----
            start_layer : int
                the earliest layer of the module
            chain : str
                specify neurons in the module
            
        Returns:
        --------
            None
        '''
        #chain = '[-1]->[-1,-2]->[-1]->[-1]'
        groups = chain.split('->')
        n_total_layers = len(groups)//2
        #start_layer = 0

        for l in range(n_total_layers):
            current_layer = cl = start_layer + l
            id_in = [int(i) for i in groups[2*l][1:-1].split(',')]
            id_out = [int(i) for i in groups[2*l+1][1:-1].split(',')]

            in_dim = self.width_in[cl]
            out_dim = self.width_out[cl+1]
            id_in_other = list(set(range(in_dim)) - set(id_in))
            id_out_other = list(set(range(out_dim)) - set(id_out))
            self.act_fun[cl].mask.data[np.ix_(id_in_other,id_out)] = 0.
            self.act_fun[cl].mask.data[np.ix_(id_in,id_out_other)] = 0.
            
        self.log_history('module')
        
        
    def speed(self, compile=True):
        '''
        turn on KAN's speed mode
        '''
        if compile == True:
            return torch.compile(self)
        else:
            return self
        
    def get_act(self, x=None):
        '''
        collect intermidate activations
        '''
        if isinstance(x, dict):
            x = x['train_input']
        if x == None:
            if self.cache_data != None:
                x = self.cache_data
            else:
                raise Exception("missing input data x")
        self.forward(x)
        
    def get_fun(self, l, i, j):
        '''
        get function (l,i,j)
        '''
        inputs = self.spline_preacts[l][:,j,i].cpu().detach().numpy()
        outputs = self.spline_postacts[l][:,j,i].cpu().detach().numpy()
        # they are not ordered yet
        rank = np.argsort(inputs)
        inputs = inputs[rank]
        outputs = outputs[rank]
        return inputs, outputs
        
    @property
    def n_edge(self):
        '''
        the number of active edges
        '''
        depth = len(self.act_fun)
        complexity = 0
        for l in range(depth):
            complexity += torch.sum(self.act_fun[l].mask > 0.)
        return complexity.item()
    
    def evaluate(self, dataset):
        evaluation = {}
        evaluation['test_loss'] = torch.sqrt(torch.mean((self.forward(dataset['test_input']) - dataset['test_label'])**2)).item()
        evaluation['n_edge'] = self.n_edge
        evaluation['n_grid'] = self.grid
        # add other metrics (maybe accuracy)
        return evaluation
    
    def swap(self, l, i1, i2, log_history=True):
        
        self.act_fun[l-1].swap(i1,i2,mode='out')
        self.act_fun[l].swap(i1,i2,mode='in')
        
        def swap_(data, i1, i2):
            data[i1], data[i2] = data[i2], data[i1]
            
        swap_(self.node_scale[l-1].data, i1, i2)
        swap_(self.node_bias[l-1].data, i1, i2)
        swap_(self.subnode_scale[l-1].data, i1, i2)
        swap_(self.subnode_bias[l-1].data, i1, i2)
        
        if log_history:
            self.log_history('swap')
            
    @property
    def connection_cost(self):
        
        cc = 0.
        for t in self.edge_scores:
            
            def get_coordinate(n):
                return torch.linspace(0,1,steps=n+1, device=self.device)[:n] + 1/(2*n)

            in_dim = t.shape[0]
            x_in = get_coordinate(in_dim)

            out_dim = t.shape[1]
            x_out = get_coordinate(out_dim)

            dist = torch.abs(x_in[:,None] - x_out[None,:])
            cc += torch.sum(dist * t)

        return cc
    
    def auto_swap_l(self, l):

        num = self.width_in[1]
        for i in range(num):
            ccs = []
            for j in range(num):
                self.swap(l,i,j,log_history=False)
                self.get_act()
                self.attribute()
                cc = self.connection_cost.detach().clone()
                ccs.append(cc)
                self.swap(l,i,j,log_history=False)
            j = torch.argmin(torch.tensor(ccs))
            self.swap(l,i,j,log_history=False)

    def auto_swap(self):
        '''
        automatically swap neurons such as connection costs are minimized
        '''
        depth = self.depth
        for l in range(1, depth):
            self.auto_swap_l(l)
            
        self.log_history('auto_swap')

KAN = MultKAN
