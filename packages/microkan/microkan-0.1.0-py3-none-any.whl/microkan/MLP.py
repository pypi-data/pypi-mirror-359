import torch
import torch.nn as nn
import numpy as np
from tqdm import tqdm
from .LBFGS import LBFGS

seed = 0
torch.manual_seed(seed)

class MLP(nn.Module):

    def __init__(self, width, act=torch.nn.SiLU(), save_act=True, seed=0, device='cpu'):
        super(MLP, self).__init__()

        torch.manual_seed(seed)

        linears = []
        self.width = width
        self.depth = depth = len(width) - 1
        for i in range(depth):
            linears.append(nn.Linear(width[i], width[i+1]))
        self.linears = nn.ModuleList(linears)

        #if activation == 'silu':
        self.act_fun = act
        self.save_act = save_act
        self.acts = None

        self.cache_data = None

        self.device = device
        self.to(device)


    def to(self, device):
        super(MLP, self).to(device)
        self.device = device

        return self


    def get_act(self, x=None):
        if isinstance(x, dict):
            x = x['train_input']
        if x == None:
            if self.cache_data != None:
                x = self.cache_data
            else:
                raise Exception("missing input data x")
        self.forward(x)

    @property
    def w(self):
        return [self.linears[l].weight for l in range(self.depth)]

    def forward(self, x):

        # cache data
        self.cache_data = x

        self.acts = []
        self.acts_scale = []
        self.wa_forward = []
        self.a_forward = []

        for i in range(self.depth):
            x = self.linears[i](x)
            if i < self.depth - 1:
                x = self.act_fun(x)
        return x

    def attribute(self):
        if self.acts == None:
            self.get_act()

        node_scores = []
        edge_scores = []

        # back propagate from the last layer
        node_score = torch.ones(self.width[-1]).requires_grad_(True).to(self.device)
        node_scores.append(node_score)

        for l in range(self.depth,0,-1):

            edge_score = torch.einsum('ij,i->ij', torch.abs(self.wa_forward[l-1]), node_score/(self.acts_scale[l-1]+1e-4))
            edge_scores.append(edge_score)

            # this might be improper for MLPs (although reasonable for KANs)
            node_score = torch.sum(edge_score, dim=0)/torch.sqrt(torch.tensor(self.width[l-1], device=self.device))
            #print(self.width[l])
            node_scores.append(node_score)

        self.node_scores = list(reversed(node_scores))
        self.edge_scores = list(reversed(edge_scores))
        self.wa_backward = self.edge_scores


    def reg(self, reg_metric, lamb_l1, lamb_entropy):

        if reg_metric == 'w':
            acts_scale = self.w
        if reg_metric == 'act':
            acts_scale = self.wa_forward
        if reg_metric == 'fa':
            acts_scale = self.wa_backward
        if reg_metric == 'a':
            acts_scale = self.acts_scale

        if len(acts_scale[0].shape) == 2:
            reg_ = 0.

            for i in range(len(acts_scale)):
                vec = acts_scale[i]
                vec = torch.abs(vec)

                l1 = torch.sum(vec)
                p_row = vec / (torch.sum(vec, dim=1, keepdim=True) + 1)
                p_col = vec / (torch.sum(vec, dim=0, keepdim=True) + 1)
                entropy_row = - torch.mean(torch.sum(p_row * torch.log2(p_row + 1e-4), dim=1))
                entropy_col = - torch.mean(torch.sum(p_col * torch.log2(p_col + 1e-4), dim=0))
                reg_ += lamb_l1 * l1 + lamb_entropy * (entropy_row + entropy_col)

        elif len(acts_scale[0].shape) == 1:

            reg_ = 0.

            for i in range(len(acts_scale)):
                vec = acts_scale[i]
                vec = torch.abs(vec)

                l1 = torch.sum(vec)
                p = vec / (torch.sum(vec) + 1)
                entropy = - torch.sum(p * torch.log2(p + 1e-4))
                reg_ += lamb_l1 * l1 + lamb_entropy * entropy

        return reg_

    def get_reg(self, reg_metric, lamb_l1, lamb_entropy):
        return self.reg(reg_metric, lamb_l1, lamb_entropy)

    def fit(self, dataset, opt="LBFGS", steps=100, log=1, lamb=0., lamb_l1=1., lamb_entropy=2., loss_fn=None, lr=1., batch=-1,
              metrics=None, in_vars=None, out_vars=None, beta=3, device='cpu', reg_metric='w', display_metrics=None):


        pbar = tqdm(range(steps), desc='description', ncols=100)

        if loss_fn == None:
            loss_fn = loss_fn_eval = lambda x, y: torch.mean((x - y) ** 2)
        else:
            loss_fn = loss_fn_eval = loss_fn

        if opt == "Adam":
            optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        elif opt == "LBFGS":
            optimizer = LBFGS(self.parameters(), lr=lr, history_size=10, line_search_fn="strong_wolfe", tolerance_grad=1e-32, tolerance_change=1e-32, tolerance_ys=1e-32)

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
            pred = self.forward(dataset['train_input'][train_id].to(self.device))
            train_loss = loss_fn(pred, dataset['train_label'][train_id].to(self.device))
            reg_ = torch.tensor(0.)
            objective = train_loss + lamb * reg_
            objective.backward()
            return objective

        for _ in pbar:

            train_id = np.random.choice(dataset['train_input'].shape[0], batch_size, replace=False)
            test_id = np.random.choice(dataset['test_input'].shape[0], batch_size_test, replace=False)

            if opt == "LBFGS":
                optimizer.step(closure)

            if opt == "Adam":
                pred = self.forward(dataset['train_input'][train_id].to(self.device))
                train_loss = loss_fn(pred, dataset['train_label'][train_id].to(self.device))

                reg_ = torch.tensor(0.)
                loss = train_loss + lamb * reg_
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            test_loss = loss_fn_eval(self.forward(dataset['test_input'][test_id].to(self.device)), dataset['test_label'][test_id].to(self.device))


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

    @property
    def connection_cost(self):

        with torch.no_grad():
            cc = 0.
            for linear in self.linears:
                t = torch.abs(linear.weight)
                def get_coordinate(n):
                    return torch.linspace(0,1,steps=n+1, device=self.device)[:n] + 1/(2*n)

                in_dim = t.shape[0]
                x_in = get_coordinate(in_dim)

                out_dim = t.shape[1]
                x_out = get_coordinate(out_dim)

                dist = torch.abs(x_in[:,None] - x_out[None,:])
                cc += torch.sum(dist * t)

        return cc

    def swap(self, l, i1, i2):

        def swap_row(data, i1, i2):
            data[i1], data[i2] = data[i2].clone(), data[i1].clone()

        def swap_col(data, i1, i2):
            data[:,i1], data[:,i2] = data[:,i2].clone(), data[:,i1].clone()

        swap_row(self.linears[l-1].weight.data, i1, i2)
        swap_row(self.linears[l-1].bias.data, i1, i2)
        swap_col(self.linears[l].weight.data, i1, i2)

    def auto_swap_l(self, l):

        num = self.width[l]
        for i in range(num):
            ccs = []
            for j in range(num):
                self.swap(l,i,j)
                self.get_act()
                self.attribute()
                cc = self.connection_cost.detach().clone()
                ccs.append(cc)
                self.swap(l,i,j)
            j = torch.argmin(torch.tensor(ccs))
            self.swap(l,i,j)

    def auto_swap(self):
        depth = self.depth
        for l in range(1, depth):
            self.auto_swap_l(l)

    def tree(self, x=None, in_var=None, style='tree', sym_th=1e-3, sep_th=1e-1, skip_sep_test=False, verbose=False):
        if x == None:
            x = self.cache_data
        plot_tree(self, x, in_var=in_var, style=style, sym_th=sym_th, sep_th=sep_th, skip_sep_test=skip_sep_test, verbose=verbose)
