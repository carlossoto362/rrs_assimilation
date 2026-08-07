from typing import Any, List, MutableMapping
import datetime

import numpy as np
from eatpy import shared

class add_noise(shared.Plugin):
    def __init__(
            self,
            path_C_squared = './C_squared.npy',
            diagnostics_in_state = ['total_chlorophyll','lightspectral_NAP','lightspectral_CDOM',\
                                    'lightspectral_Rrs425','lightspectral_Rrs450','lightspectral_Rrs500',\
                                    'lightspectral_Rrs525','lightspectral_Rrs550'], #defoult diagnostics in state.
            method = 3,   #1 -> constant covariance matrix, 2 -> use covariance matrix of state, 3 -> use correlation matrix of state.
            rho = 1,
            gamma = 0.1,
            num_obs = 1,
            num_ensemble_members = 1,
            dump_noise_slide = None,
            delta_t = 30,
            add_bias = False,
            add_R = True,
            max_rho = 12,
            no_log = False,
            spatial_var=[],
            verbose=False,
    ):
        if (method == 1) or (method == 3) :        
            self.C_squared = np.load(path_C_squared,allow_pickle=True)

            #I saved the squared root of C for the state and for 8 diagnostic variables. The main state starts at index 593.
            self.C_squared_main = self.C_squared[:,593:]
            #the diagnostics in state are added to the state in the same order as added in the function models.GOTM.
            #The variables i saved are:
            diag_state_lims = {'total_chlorophyll':[397,593],'lightspectral_NAP':[201,397],'lightspectral_CDOM':[5,201],\
                               'lightspectral_Rrs425':[4,5],'lightspectral_Rrs450':[3,4],'lightspectral_Rrs500':[2,3],\
                               'lightspectral_Rrs525':[1,2],'lightspectral_Rrs550':[0,1]}
            def var_i_function(diag_state):
                start,end = diag_state_lims[diag_state]
                var_i = self.C_squared[:,start:end]
                if len(var_i.shape) == 1:
                    var_i.reshape((var_i.shape,1))
                return var_i
            
            for diag_state in diagnostics_in_state:
                self.C_squared_main = np.append(var_i_function(diag_state),self.C_squared_main,axis=1)

            self.C_squared = self.C_squared_main
            if no_log:
                self.C_squared = np.exp(self.C_squared)

            if method == 3:
                C_shape = self.C_squared.shape
                self.D_squared = self.C_squared.std(axis=0)
            
        self.add_bias = add_bias
        self.add_R = add_R
        self.method = method
        self.rho = rho
        self.gamma = gamma
        self.num_obs = num_obs
        self.index_to_i = - np.ones(self.num_obs).astype(int)
        self.variations = - np.ones((delta_t,num_ensemble_members,self.num_obs)).astype(float)
        self.old_state = 0
        self.dump_noise_slide = dump_noise_slide
        self.m = num_ensemble_members
        self.delta_t = delta_t
        self.F_old = None
        self.max_rho=max_rho
        self.spatial_var = np.array(spatial_var)
        self.verbose = verbose

    def initialize(self, variables: MutableMapping[str, Any], *args, **kwargs):
        pass
        
    def before_analysis(
        self,
        time: datetime.datetime,
        state: np.ndarray,
        iobs: np.ndarray,
        obs: np.ndarray,
        obs_sds: np.ndarray,
        *args,
        **kwargs
    ):
        if self.method == 2:
            Q_squared = (state[...] - state[...].mean(axis=0))*np.sqrt(1/self.m)
        elif self.method == 1:
            Q_squared = (self.C_squared - self.C_squared.mean(axis=0))*np.sqrt(1/self.m)
            
        #covariance matrix C = SS^T, defining D the diagonal elements of C, then the correlation matrix is R = D^(-1/2)SS^TD^(-1/2), so his square root is D^(-1/2)S.
        elif self.method == 3:
            stds = state[...].std(axis=0)
            if (stds == 0).any():
                # #if std is zero for some variable, has zero or one correlation with all other variables. I'll 1 correlation with him self, 0 with others.
                R_squared = np.sqrt(1/(state[...].shape[0]-1))*np.ones(state.shape)
                R_squared[:,stds!=0] *= (state[:,stds!=0] - state[:,stds!=0].mean(axis=0))/state[:,stds!=0].std(axis=0)
            else:
                R_squared = np.sqrt(1/(state[...].shape[0]-1))*(state[...] - state[...].mean(axis=0))/state[...].std(axis=0)
            Q_squared = R_squared*self.D_squared

        noise = np.sqrt(self.rho) * (Q_squared.T @ np.random.standard_normal((state.shape[0],state.shape[0]))).T
        if self.dump_noise_slide:
            for slide in self.dump_noise_slide:
                noise[:,slide[0]:slide[1]] = 0
        state_new = state[...] + noise
            
            
        
        self.current_obs = obs
        spected_variations = None
        Q_vars = []
        state_var = []
        new_state_var = []
        if obs.any():
            
            len_obs = len(obs)
            F = 0 
            for j,obs_i in enumerate(iobs):
                if (self.index_to_i < 0).any():
                    for i in range(self.num_obs):
                        if self.index_to_i[i] < 0 :
                            self.index_to_i[i] = obs_i
                            self.logger.info("adding new observation")
                            break

                var_i = np.argwhere(self.index_to_i == obs_i)
                
                if (self.variations[:,:,var_i] < 0).any():
                    for i in range(self.delta_t):
                        if (self.variations[i,:,var_i]<0).any():
                            self.variations[i,:,var_i] = (obs[j] - state_new[:,obs_i])**2
                            break
                else:
                    self.variations[1:,:,var_i] = self.variations[:-1,:,var_i]
                    self.variations[0,:,var_i] = (obs[j] - state_new[:,obs_i])

                if (self.variations[:,:,var_i] < 0).any():
                    continue
                        
                spected_variations = np.array(self.variations[:,:,var_i]).T
                spected_variations = (spected_variations**2).mean(axis=1)
                
                if self.add_bias == True:
                    bias_squared = ((spected_variations).mean(axis=1))**2
                    spected_variations -= bias_squared


                mu = state[:,obs_i].mean() #Using the ensemble to estimate the average. It workes just with the last one
                vf = state[:,obs_i] - mu
                vo = self.old_state[:,obs_i] - mu
                tangent = np.sum(vo*(vf-vo))/(np.sum(vo**2))#seam to work fine only with the last two values of deterministic_steps
                
                #sigma_squared =  spected_variations *  tangent
                Q_vars.append((Q_squared[:,obs_i].var()))
                state_var.append(state[:,obs_i].var())
                new_state_var.append(state_new[:,obs_i].var())
                #self.logger.info("   - " + str(spected_variations.mean()) + " " + str(tangent) + " " + str(np.sqrt(sigma_squared)) + " " + str(delta_rho) + " " + str(Q_squared[:,obs_i].var()) + " " + str(obs_i) + " " + str(noise[:,obs_i].var()))
                
                #self.logger.info("#######----$$$$$ "+ str(spected_variations.mean()) + " " + str(obs_sds[j]))
                if len(self.spatial_var) != 0:
                    spected_variations += self.spatial_var[var_i]
                    
                if self.add_R == True:
                    spected_variations = np.maximum(0,spected_variations -  obs_sds[j]**2)
                if len(self.spatial_var) != 0:
                    spected_variations += self.spatial_var[var_i]
                    
                spected_variations = np.maximum(0,spected_variations)
                #new_rho += np.maximum(0,(spected_variations) *  np.abs(tangent) -state[:,obs_i].var())
                F += ((spected_variations) *  np.abs(tangent) - state_new[:,obs_i].var())

                if self.verbose:
                    self.logger.info("spected_variations: "+str(np.mean(spected_variations)))
                
                

            F = np.mean(F)
            #self.logger.info("###########----" + str(delta_rho) + " " + str(1/np.sum(Q_vars)))
            if F != 0:
                #using newton method:
                #F /= (2*np.sum(Q_vars)*state.shape[0])

                self.logger.info("delta_rho: "+str(F))
                #self.logger.info("theoretical_rho: " +str(self.rho + F) )
                self.rho = np.minimum(self.max_rho,np.maximum(0,self.rho + self.gamma*F)) #I want to avoid non linear effects, appearing around this value. 
                #if spected_variations:
                
                self.logger.info("new_rho: "+ str(self.rho))


        state[...] = state_new
        self.old_state = state_new.copy()


    def after_analysis(self, *args, **kwargs):
        pass
