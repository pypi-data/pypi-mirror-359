from ...environment.optimizer.basic_optimizer import Basic_Optimizer
# from optimizer.operators import clipping
import numpy as np


class SAHLPSO(Basic_Optimizer):
    """
    # Introduction
    Self-Adaptive two roles hybrid learn-ing strategies-based particle swarm optimization.It uses exploration-role and exploitation-role learning strategies with self-adaptively updating parameters manner.
    # Original paper
    "[**Self-Adaptive two roles hybrid learning strategies-based particle swarm optimization**](https://www.sciencedirect.com/science/article/pii/S0020025521006988)." Information Sciences 578 (2021): 457-481.
    """
    
    def __init__(self, config):
        """
        # Introduction
        Initializes the SAHLPSO (Self-Adaptive Hybrid Learning Particle Swarm Optimization) algorithm with the provided configuration parameters.
        # Args:
            - config (object): Configuration object containing algorithm parameters.
                - The Attributes needed for the SAHLPSO optimizer in config are the following:
                    - maxFEs (int): Maximum number of function evaluations allowed.Default value depends on the type of the problem.
                    - n_logpoint (int): Number of log points for tracking progress. Default is 50.
                    - log_interval (int): Interval at which logs are recorded. Default is maxFEs // n_logpoint.
                    - full_meta_data (bool): Flag indicating whether to store complete solution history. Default is False.
                    - seed (int): Random seed for reproducibility. Used for initializing positions and velocities.
        # Attributes:
        - NP (int): Number of particles in the swarm (default: 40).
        - lb (float): Lower bound for particle positions (default: -5).
        - ub (float): Upper bound for particle positions (default: 5).
        - v_max (float): Maximum velocity for particles (default: 1).
        - H_cr (int): Number of crossover rates (default: 5).
        - M_cr (list of float): List of crossover rates.
        - H_ls (int): Number of local search strategies (default: 15).
        - M_ls (range): Range of local search strategies.
        - LP (int): Learning period (default: 5).
        - Lg (float): Learning gain (default: 0.2).
        - p (float): Probability parameter (default: 0.2).
        - c1 (float): Cognitive acceleration coefficient (default: 1.49445).
        - log_interval (int): Logging interval, taken from `config`.
        - full_meta_data (bool): Flag indicating whether to store full meta data, taken from `config`.
        """
        
        super().__init__(config)
        self.config = config
        self.NP, self.maxFEs, self.lb, self.ub, self.v_max = 40, config.maxFEs, -5, 5, 1
        self.H_cr = 5
        self.M_cr = [0.0001,0.0005,0.001,0.005,0.01,0.05,0.1,0.5]
        self.H_ls = 15
        self.M_ls = range(1,16)
        self.LP = 5
        self.Lg = 0.2
        self.p=0.2
        self.c1 = 1.49445
        self.log_interval = config.log_interval
        self.full_meta_data = config.full_meta_data
        
    def __str__(self):  
        """
        # Introduction
        Returns the string representation of the SAHLPSO class.
        # Returns:
        - str: The string 'SAHLPSO'.
        """
        
        return 'SAHLPSO'

    def run_episode(self,problem):
        """
        # Introduction
        Executes a single optimization episode using the Self-Adaptive History Learning Particle Swarm Optimization (SAHLPSO) algorithm on the provided problem instance. The method manages the population, velocity, and adaptive parameters, and logs the optimization progress.
        # Args:
        - problem (object): An optimization problem instance that must provide the following attributes and methods:
            - `dim` (int): Dimensionality of the problem.
            - `lb` (array-like): Lower bounds for each dimension.
            - `ub` (array-like): Upper bounds for each dimension.
            - `optimum` (float or None): Known optimum value for the problem (optional).
            - `eval(X)` (callable): Function to evaluate the fitness of a population `X`.
        # Returns:
        - dict: A dictionary containing:
            - 'cost' (list): The best cost (fitness) found at each logging interval.
            - 'fes' (int): The total number of function evaluations performed.
            - 'metadata' (dict, optional): If `self.full_meta_data` is True, includes:
                - 'X' (list): History of population positions.
                - 'Cost' (list): History of population costs.
        # Notes:
        - The method adapts crossover and learning strategies based on historical success rates.
        - Population size is dynamically reduced during the run.
        - Logging intervals and meta-data collection are controlled by the class configuration.
        """
        
        self.dim = problem.dim
        self.lb = problem.lb
        self.ub = problem.ub
        if self.full_meta_data:
            self.meta_Cost = []
            self.meta_X = []
        G, fes, NP, H_cr, H_ls = 1, 0, self.NP, self.H_cr, self.H_ls
        V = -self.v_max + 2 * self.v_max * self.rng.rand(NP, self.dim)
        X = self.lb + (self.ub - self.lb) * self.rng.rand(NP, self.dim)
        if problem.optimum is None:
            f_X = problem.eval(X)
        else:
            f_X = problem.eval(X) - problem.optimum
        if self.full_meta_data:
            self.meta_Cost.append(f_X)
            self.meta_X.append(X)
        w = 0.9 * np.ones(NP)
        fes += NP
        pBest,pBest_cost,A = X.copy(), f_X.copy(),[]
        for i in range(NP):
            A.append([pBest[i]])
        gBest = X[np.argmin(f_X)]
        gBest_cost = np.min(f_X)

        log_index = 1
        cost = [gBest_cost]

        P_cr = np.ones(H_cr) / H_cr
        nf_cr = np.zeros(H_cr)
        ns_cr = np.zeros(H_cr)
        P_ls = np.ones(H_ls) / H_ls
        nf_ls = np.zeros(H_ls)
        ns_ls = np.zeros(H_ls)
        remain_index = np.array(range(NP))
        selected_indiv_index = self.rng.permutation(remain_index)[:int(self.Lg * NP)]
        while fes < self.maxFEs :
            
            for i in remain_index:
                cr, ls = 0, 0 # start generate exemplar
                cr_index, ls_index = 0,0
                if (G%self.LP) or (G==1):
                    cr_index = self.rng.choice(range(H_cr),p=P_cr)
                    cr = self.M_cr[cr_index]
                    ls_index = self.rng.choice(range(H_ls),p=P_ls)
                    ls = self.M_ls[ls_index]
                #exploration indiv
                if i in selected_indiv_index:
                    mn = self.rng.choice(remain_index,2)
                    m,n=mn[0],mn[1]
                    o = pBest[m] if f_X[m] < f_X[n] else pBest[n]
                    if (G-ls) >= 0:
                        history_pbest = A[i][G-ls-1]
                    else:
                        history_pbest = A[i][-1]
                else:
                    best_p_index = np.argsort(pBest_cost)[:max(1, int(self.p *NP))]
                    o = pBest[self.rng.choice(best_p_index)]
                    history_pbest = pBest[i]
                # execute crossover in each dimensional
                mask_crossover = self.rng.rand(self.dim) < cr
                e = history_pbest
                e[mask_crossover] = o[mask_crossover]
                if i not in selected_indiv_index:
                    rnd1 = self.rng.rand(self.dim)
                    e =  rnd1 * e + (1 - rnd1) * gBest # end generate exemplar

                # update cr and ls selection times
                nf_cr[cr_index] += 1
                nf_ls[ls_index] += 1
                # generate velocity V and BC(V)
                V[i] = w[i] * V[i] + self.c1 * self.rng.rand(self.dim) * (e - X[i])
                V[i] = np.clip(V[i], -self.v_max, self.v_max)
                # generate new X and BC(X)
                X[i] = np.clip(X[i] + V[i], self.lb, self.ub)
                # evaluate X
                if problem.optimum is None:
                    f_X[i] = problem.eval(X[i])
                else:
                    f_X[i] = problem.eval(X[i]) - problem.optimum
                    
                fes += 1
                if f_X[i] < pBest_cost[i]:
                    pBest[i] = X[i]
                    if f_X[i] < gBest_cost:
                        gBest = X[i]
                        gBest_cost = f_X[i]
                    # update cr and ls success times
                    ns_cr[cr_index] += 1
                    ns_ls[ls_index] += 1
                else:
                    rnd2 = self.rng.rand()
                    if rnd2 < 0.5:
                        w[i] = 0.7 + 0.1 *self.rng.standard_cauchy()
                    else:
                        w[i] = 0.3 + 0.1 * self.rng.standard_cauchy()
                    w[i] = np.clip(w[i], 0.2,0.9)
                A[i].append(pBest[i])

                if fes >= log_index * self.log_interval:
                    log_index += 1
                    cost.append(gBest_cost)

            if self.full_meta_data:
                self.meta_Cost.append(f_X.copy())
                self.meta_X.append(X.copy())
            
            # after a generation update related statics
            if G % self.LP == 0:

                S_cr = np.zeros(H_cr)
                mask = nf_cr != 0
                S_cr[mask] = ns_cr[mask] / nf_cr[mask]
                # update P_cr
                if np.sum(S_cr) == 0:
                    if H_cr < len(self.M_cr):
                        H_cr += 1
                        nf_cr = np.append(nf_cr, 0)
                        ns_cr = np.append(ns_cr, 0)
                    P_cr = np.ones(H_cr) / H_cr
                else:
                    P_cr = S_cr / (np.sum(S_cr) + 1e-20)

                # update P_ls
                S_ls = np.zeros(H_ls)
                mask = nf_ls != 0
                S_ls[mask] = ns_ls[mask] / nf_ls[mask]
                if np.sum(S_ls) == 0:
                    P_ls = np.ones(H_ls) / H_ls
                else:
                    P_ls = S_ls / np.sum(S_ls)
                

            # population size reduction
            NP_ = round((4 - self.NP) * fes / self.maxFEs + self.NP)
            NP_ = max(NP_, 5) 
            if NP_ < NP:
                remain_index = np.argsort(pBest_cost)[:NP_]
                NP = NP_

            G += 1

        if len(cost) >= self.config.n_logpoint + 1:
            cost[-1] = gBest_cost
        else:
            while len(cost) < self.config.n_logpoint + 1:
                cost.append(gBest_cost)
        results = {'cost': cost, 'fes': fes}

        if self.full_meta_data:
            metadata = {'X':self.meta_X, 'Cost':self.meta_Cost}
            results['metadata'] = metadata
        # 与agent一致，去除return，加上metadata
        return results
