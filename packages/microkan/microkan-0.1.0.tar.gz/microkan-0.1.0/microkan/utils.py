import numpy as np
import torch
import re
import torch
import numpy as np
import random
import os

def set_seed(seed: int):
    """
    Sets the seed for all relevant random number generators to ensure reproducibility.
    """
    # Set seed for Python's random module
    random.seed(seed)

    # Set seed for NumPy
    np.random.seed(seed)

    # Set seed for PyTorch on CPU and GPU
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)  # for multi-GPU.

    # Configure PyTorch to use deterministic algorithms
    # This is the crucial part for L-BFGS on GPU
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # For some PyTorch versions, this is also needed
    # It might throw an error if the operation doesn't have a deterministic implementation
    try:
        torch.use_deterministic_algorithms(True)
    except Exception as e:
        print(f"Could not set deterministic algorithms: {e}")

    # This environment variable can also help with determinism in CUDA
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'


def create_dataset(f, 
                   n_var=2, 
                   f_mode = 'col',
                   ranges = [-1,1],
                   train_num=1000, 
                   test_num=1000,
                   normalize_input=False,
                   normalize_label=False,
                   device='cpu',
                   seed=0):
    '''
    create dataset
    
    Args:
    -----
        f : function
            the formula used to create the synthetic dataset
        ranges : list or np.array; shape (2,) or (n_var, 2)
            the range of input variables. Default: [-1,1].
        train_num : int
            the number of training samples. Default: 1000.
        test_num : int
            the number of test samples. Default: 1000.
        normalize_input : bool
            If True, apply normalization to inputs. Default: False.
        normalize_label : bool
            If True, apply normalization to labels. Default: False.
        device : str
            device. Default: 'cpu'.
        seed : int
            random seed. Default: 0.
        
    Returns:
    --------
        dataset : dic
            Train/test inputs/labels are dataset['train_input'], dataset['train_label'],
                        dataset['test_input'], dataset['test_label']
         
    Example
    -------
    >>> f = lambda x: torch.exp(torch.sin(torch.pi*x[:,[0]]) + x[:,[1]]**2)
    >>> dataset = create_dataset(f, n_var=2, train_num=100)
    >>> dataset['train_input'].shape
    torch.Size([100, 2])
    '''

    np.random.seed(seed)
    torch.manual_seed(seed)

    if len(np.array(ranges).shape) == 1:
        ranges = np.array(ranges * n_var).reshape(n_var,2)
    else:
        ranges = np.array(ranges)
        
    
    train_input = torch.zeros(train_num, n_var)
    test_input = torch.zeros(test_num, n_var)
    for i in range(n_var):
        train_input[:,i] = torch.rand(train_num,)*(ranges[i,1]-ranges[i,0])+ranges[i,0]
        test_input[:,i] = torch.rand(test_num,)*(ranges[i,1]-ranges[i,0])+ranges[i,0]
                
    if f_mode == 'col':
        train_label = f(train_input)
        test_label = f(test_input)
    elif f_mode == 'row':
        train_label = f(train_input.T)
        test_label = f(test_input.T)
    else:
        print(f'f_mode {f_mode} not recognized')
        
    # if has only 1 dimension
    if len(train_label.shape) == 1:
        train_label = train_label.unsqueeze(dim=1)
        test_label = test_label.unsqueeze(dim=1)
        
    def normalize(data, mean, std):
            return (data-mean)/std
            
    if normalize_input == True:
        mean_input = torch.mean(train_input, dim=0, keepdim=True)
        std_input = torch.std(train_input, dim=0, keepdim=True)
        train_input = normalize(train_input, mean_input, std_input)
        test_input = normalize(test_input, mean_input, std_input)
        
    if normalize_label == True:
        mean_label = torch.mean(train_label, dim=0, keepdim=True)
        std_label = torch.std(train_label, dim=0, keepdim=True)
        train_label = normalize(train_label, mean_label, std_label)
        test_label = normalize(test_label, mean_label, std_label)

    dataset = {}
    dataset['train_input'] = train_input.to(device)
    dataset['test_input'] = test_input.to(device)

    dataset['train_label'] = train_label.to(device)
    dataset['test_label'] = test_label.to(device)

    return dataset




  
def batch_jacobian(func, x, create_graph=False, mode='scalar'):
    '''
    jacobian
    
    Args:
    -----
        func : function or model
        x : inputs
        create_graph : bool
        
    Returns:
    --------
        jacobian
    
    Example
    -------
    >>> from kan.utils import batch_jacobian
    >>> x = torch.normal(0,1,size=(100,2))
    >>> model = lambda x: x[:,[0]] + x[:,[1]]
    >>> batch_jacobian(model, x)
    '''
    # x in shape (Batch, Length)
    def _func_sum(x):
        return func(x).sum(dim=0)
    if mode == 'scalar':
        return torch.autograd.functional.jacobian(_func_sum, x, create_graph=create_graph)[0]
    elif mode == 'vector':
        return torch.autograd.functional.jacobian(_func_sum, x, create_graph=create_graph).permute(1,0,2)

def batch_hessian(model, x, create_graph=False):
    '''
    hessian
    
    Args:
    -----
        func : function or model
        x : inputs
        create_graph : bool
        
    Returns:
    --------
        jacobian
    
    Example
    -------
    >>> from kan.utils import batch_hessian
    >>> x = torch.normal(0,1,size=(100,2))
    >>> model = lambda x: x[:,[0]]**2 + x[:,[1]]**2
    >>> batch_hessian(model, x)
    '''
    # x in shape (Batch, Length)
    jac = lambda x: batch_jacobian(model, x, create_graph=True)
    def _jac_sum(x):
        return jac(x).sum(dim=0)
    return torch.autograd.functional.jacobian(_jac_sum, x, create_graph=create_graph).permute(1,0,2)


def create_dataset_from_data(inputs, labels, train_ratio=0.8, device='cpu'):
    '''
    create dataset from data
    
    Args:
    -----
        inputs : 2D torch.float
        labels : 2D torch.float
        train_ratio : float
            the ratio of training fraction
        device : str
        
    Returns:
    --------
        dataset (dictionary)
    
    Example
    -------
    >>> from kan.utils import create_dataset_from_data
    >>> x = torch.normal(0,1,size=(100,2))
    >>> y = torch.normal(0,1,size=(100,1))
    >>> dataset = create_dataset_from_data(x, y)
    >>> dataset['train_input'].shape
    '''
    num = inputs.shape[0]
    train_id = np.random.choice(num, int(num*train_ratio), replace=False)
    test_id = list(set(np.arange(num)) - set(train_id))
    dataset = {}
    dataset['train_input'] = inputs[train_id].detach().to(device)
    dataset['test_input'] = inputs[test_id].detach().to(device)
    dataset['train_label'] = labels[train_id].detach().to(device)
    dataset['test_label'] = labels[test_id].detach().to(device)
    
    return dataset


def get_derivative(model, inputs, labels, derivative='hessian', loss_mode='pred', reg_metric='w', lamb=0., lamb_l1=1., lamb_entropy=0.):
    '''
    compute the jacobian/hessian of loss wrt to model parameters
    
    Args:
    -----
        inputs : 2D torch.float
        labels : 2D torch.float
        derivative : str
            'jacobian' or 'hessian'
        device : str
        
    Returns:
    --------
        jacobian or hessian
    '''
    def get_mapping(model):

        mapping = {}
        name = 'model1'

        keys = list(model.state_dict().keys())
        for key in keys:

            y = re.findall(".[0-9]+", key)
            if len(y) > 0:
                y = y[0][1:]
                x = re.split(".[0-9]+", key)
                mapping[key] = name + '.' + x[0] + '[' + y + ']' + x[1]


            y = re.findall("_[0-9]+", key)
            if len(y) > 0:
                y = y[0][1:]
                x = re.split(".[0-9]+", key)
                mapping[key] = name + '.' + x[0] + '[' + y + ']'

        return mapping

    
    #model1 = copy.deepcopy(model)
    model1 = model.copy()
    mapping = get_mapping(model)
   
    # collect keys and shapes
    keys = list(model.state_dict().keys())
    shapes = []

    for params in model.parameters():
        shapes.append(params.shape)


    # turn a flattened vector to model params
    def param2statedict(p, keys, shapes):

        new_state_dict = {}

        start = 0
        n_group = len(keys)
        for i in range(n_group):
            shape = shapes[i]
            n_params = torch.prod(torch.tensor(shape))
            new_state_dict[keys[i]] = p[start:start+n_params].reshape(shape)
            start += n_params

        return new_state_dict
    
    def differentiable_load_state_dict(mapping, state_dict, model1):

        for key in keys:
            if mapping[key][-1] != ']':
                exec(f"del {mapping[key]}")
            exec(f"{mapping[key]} = state_dict[key]")
            

    # input: p, output: output
    def get_param2loss_fun(inputs, labels):

        def param2loss_fun(p):

            p = p[0]
            state_dict = param2statedict(p, keys, shapes)
            # this step is non-differentiable
            #model.load_state_dict(state_dict)
            differentiable_load_state_dict(mapping, state_dict, model1)
            if loss_mode == 'pred':
                pred_loss = torch.mean((model1(inputs) - labels)**2, dim=(0,1), keepdim=True)
                loss = pred_loss
            elif loss_mode == 'reg':
                reg_loss = model1.get_reg(reg_metric=reg_metric, lamb_l1=lamb_l1, lamb_entropy=lamb_entropy) * torch.ones(1,1)
                loss = reg_loss
            elif loss_mode == 'all':
                pred_loss = torch.mean((model1(inputs) - labels)**2, dim=(0,1), keepdim=True)
                reg_loss = model1.get_reg(reg_metric=reg_metric, lamb_l1=lamb_l1, lamb_entropy=lamb_entropy) * torch.ones(1,1)
                loss = pred_loss + lamb * reg_loss
            return loss

        return param2loss_fun
    
    fun = get_param2loss_fun(inputs, labels)    
    p = model2param(model)[None,:]
    if derivative == 'hessian':
        result = batch_hessian(fun, p)
    elif derivative == 'jacobian':
        result = batch_jacobian(fun, p)
    return result

def model2param(model):
    '''
    turn model parameters into a flattened vector
    '''
    p = torch.tensor([]).to(model.device)
    for params in model.parameters():
        p = torch.cat([p, params.reshape(-1,)], dim=0)
    return p
