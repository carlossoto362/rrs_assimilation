from typing import Any, List, MutableMapping
import datetime
import os

import numpy as np
import netCDF4 as nc

from eatpy import shared
import sys

class Log(shared.Plugin):
    def __init__(
            self,
            *variable_names,
            transform_obs: bool = False,
            minimum: float = -np.inf,
            log10: bool = False,
            max_nc = None,
            verbose = False,
            no_log = False,
            exp_obs: bool = False,
            
    ):
        self.variable_names = frozenset(variable_names)
        self.variable_metadata: List[Any] = []
        self.transform_obs = transform_obs
        self.minimum = minimum
        self.log10 = log10
        self.exp_obs = exp_obs
        if type(max_nc) != type(None):
            self.max_nc = nc.Dataset(max_nc)
        else:
            self.max_nc = None
        self.backward = (lambda x: 10.0 ** x) if self.log10 else np.exp
        if no_log:
            self.backward = (lambda x: x)
        self.verbose = verbose
        self.no_log = no_log

    def initialize(self, variables: MutableMapping[str, Any], *args, **kwargs):
        for name in self.variable_names:
            variables[name]['name'] = name
            self.variable_metadata.append(variables[name])

            
    def forward(self,x):
        if self.no_log:
            return x
        if np.ma.isMaskedArray(x):
            if self.log10:
                return np.ma.log10(x)
            else:
                return np.ma.log(x)
        else:
            if self.log10:
                return np.log10(x)
            else:
                return np.log(x)

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
        if self.verbose == True:
            self.original = {}
        for j,metadata in enumerate(self.variable_metadata):
            
            if not np.isfinite(metadata['data']).all():
                self.logger.info(np.argwhere(~np.isfinite(metadata['data'])))
                self.logger.info(metadata['name'])
                self.logger.info(self.variable_metadata)
                self.logger.error("Non-finite values in ensemble state")
                raise Exception("non-finite values in model state or observations")

                
            affected_obs = (iobs >= metadata["start"]) & (iobs < metadata["stop"])
            
            if self.transform_obs and affected_obs.any():
                # Transform mean and sd of observations,
                # assuming their distribution is log-normal
                mean = np.maximum(obs[affected_obs], self.minimum)
                sd = obs_sds[affected_obs]
                sigma2 = np.log((sd / mean) ** 2 + 1.0)
                mu = np.log(mean) - 0.5 * sigma2
                sigma = np.sqrt(sigma2)
                if self.log10:
                    mu /= np.log(10.0)
                    sigma /= np.log(10.0)
                obs[affected_obs] = mu
                obs_sds[affected_obs] = sigma
                
            if self.exp_obs:
                mean = np.exp(obs[affected_obs] + (obs_sds[affected_obs]**2)/2)
                sigma = (np.exp(obs_sds[affected_obs]**2)-1)*np.exp(2*obs_sds[affected_obs]+obs_sds[affected_obs]**2)
                obs[affected_obs] = mean
                obs_sds[affected_obs] = np.sqrt(sigma)

            #################cheking simple way of removing too small values, but keeping same mean and std. ##########
            mask_data = np.ma.array(metadata['data'][...].copy(),mask = (metadata['data']==0))
            mask_data = self.forward(mask_data)
            mu = np.ma.mean(mask_data,axis=0)
            sigma = np.ma.std(mask_data,axis=0)
            
            metadata["data"][...] = np.maximum(metadata['data'][...],np.random.rand(*metadata['data'].shape)*(0.2 *self.minimum) + 0.9*self.minimum)
            metadata['data'][...] = self.forward(metadata['data'][...])

            mu_new = np.mean(metadata['data'][...],axis=0)
            sigma_new = np.std(metadata['data'][...],axis=0)

            if (sigma == 0).any():
                for depth in range(metadata['data'].shape[1]):
                    if sigma[depth] != 0:
                        metadata['data'][:,depth] = ((metadata['data'][:,depth] - mu_new[depth])/sigma_new[depth])*sigma[depth] + mu[depth]
                    else:
                        metadata['data'][:,depth] = metadata['data'][:,depth] - mu_new[depth] + mu[depth] # if has zero std, ill leave the fictitious noice. 
                        
            else:
                metadata['data'][...] = ((metadata['data'][...] - mu_new)/sigma_new)*sigma + mu
            ########################################################################################################

            if self.verbose == True:
                self.original[metadata['name']] = self.backward(np.copy(metadata['data']))
            
    def after_analysis(self, *args, **kwargs):
                    
        for metadata in self.variable_metadata:
            metadata["data"][...] = self.backward(metadata["data"][...])

            if type(self.max_nc) != type(None):
                try:

                    metadata["data"][...] = np.minimum( np.maximum(self.max_nc[metadata["name"]][0],4),metadata["data"][...])
                    metadata["data"][...] = np.maximum( np.maximum(self.max_nc[metadata["name"]][1],1.0e-9),metadata["data"][...])
                except:
                    pass

            if self.verbose:
                self.logger.info('before: ' + metadata['name'] + ' '  + str(self.original[metadata['name']][...].mean(axis=0)[-1]))
                self.logger.info('after: ' + metadata['name'] + ' '  + str(metadata['data'][...].mean(axis=0)[-1]))


                    
