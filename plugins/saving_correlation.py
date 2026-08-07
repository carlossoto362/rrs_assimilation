from typing import Any, List, MutableMapping
import datetime

import numpy as np
from eatpy import shared

class save_corr(shared.Plugin):
    def __init__(
            self,
            *variable_names,
            total_iterations = 24,
            save_max = False,
            save_mean = False,
            save_min = False,
            output_path = '.'
    ):
        self.variable_names = frozenset(variable_names)
        self.variable_metadata: List[Any] = []
        self.cov = 0
        self.current_iter = 0
        self.total_iterations = total_iterations
        self.save_mean = save_mean,
        self.save_max = save_max,
        self.save_min = save_min

        if self.save_mean:
            self.mean = 0
        if self.save_max:
            self.max = 0
        if self.save_min:
            self.min = 1e9

        self.output_path = output_path

    def initialize(self, variables: MutableMapping[str, Any], *args, **kwargs):
        for name in self.variable_names:
            variables[name]['name'] = name
            self.variable_metadata.append(variables[name])

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
            
        self.cov += (state[...] - state[...].mean(axis=0))
        if self.save_mean:
            self.mean += state[...]
        if self.save_max:
            self.max = np.maximum(state[...],self.max)
        if self.save_min:
            self.min = np.minimum(state[...],self.min)
        
        self.current_iter += 1
        
        if self.current_iter == self.total_iterations - 2:
            self.cov /= self.current_iter - 1
            np.save(self.output_path + "/square_cov.npy",self.cov)

            if self.save_mean:
                self.mean /= self.current_iter - 1
                np.save(self.output_path + "/average.npy",self.mean)
            if self.save_max:
                np.save(self.output_path + "/max_values.npy",self.max)
            if self.save_min:
                np.save(self.output_path + "/min_values.npy",self.min)

            with open(self.output_path + "/metadata_info.csv",'w') as myfile:
                myfile.write('name,start,stop\n')
                for j,metadata in enumerate(self.variable_metadata):
                    myfile.write(metadata["name"]+','+str(metadata['start'])+','+str(metadata['stop'])+'\n')
            

    def after_analysis(self, *args, **kwargs):
        pass
