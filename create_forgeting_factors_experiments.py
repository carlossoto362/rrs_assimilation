import os
import sys
import numpy as np
import argparse

def writing_run(home_path,diagnostics_in_state=['total_chlorophyll'],obs_paths=['chla_inverted.txt'],forget=0.95,observations_z=[-26],exp_obs=True,no_log=True):
    
    diag_state_str = "['"
    for diag_state in diagnostics_in_state:
        if diag_state != diagnostics_in_state[-1]:
            diag_state_str += diag_state + "','"
        else:
            diag_state_str += diag_state + "'"
    diag_state_str += "]"

    obs_text = ""
    for i in range(len(obs_paths)):
        obs_text += "experiment.add_observations('"+diagnostics_in_state[i]+"["+str(observations_z[i])+"]"+"', '"+home_path+"/observation/"+obs_paths[i]+"')\n"
    
    text = """

import eatpy,sys,os,datetime
sys.path.append('"""+home_path+"""/plugins')
import transform_clean as toun

experiment = eatpy.models.GOTM(
    diagnostics_in_state="""+diag_state_str+""",
    start=datetime.datetime(2001, 1, 1), stop=datetime.datetime(2010, 12, 31)
)
filter = eatpy.PDAF(eatpy.pdaf.FilterType.ESTKF,forget=""" +str(forget) +""")

bgc_variables = ['O4_n','Z6_p','R8_s','R6_n','Z4_p','B1_n','R6_p','Z6_n','O3_c','R1_p','R3_c','Z3_p','Z4_c','B1_c','R2_c','R1_c','Z5_n','O5_c','O2_o','Z6_c','Z5_c','B1_p','N6_r','O3h_h','Z5_p','R6_s','Z3_n','R8_n','Z3_c','R8_p','Z4_n','R1_n','N1_p','N3_n','N4_n','N5_s','R6_c','R8_c','X1_c','X2_c','X3_c','P1_c','P1_n','P1_p','P1_Chl','P1_s','P2_c','P2_n','P2_p','P2_Chl','P3_c','P3_n','P3_p','P3_Chl','P4_c','P4_n','P4_p','P4_Chl']

bgc_variables += """+diag_state_str+"""

experiment.add_plugin(
    eatpy.plugins.select.Select(include=bgc_variables)
)
experiment.add_plugin(eatpy.plugins.check.Finite())
experiment.add_plugin(
    toun.Log(
        *bgc_variables,
        transform_obs=False,
        minimum=1e-9,
        log10 = False,
        max_nc = '"""+home_path+"""/plugins/ncfile_ranges.nc',
        exp_obs = """+str(exp_obs)+""",
        no_log = """ + str(no_log)+""",
    )
)
"""+obs_text+"""
experiment.run(filter)
    """
    return text

def creating_work_space(home_path,da_path,diagnostics_in_state,obs_paths,observations_z,forget,exp_obs=True,no_log=True,num_ensembles=2):
    path_ = da_path + '/factor_{:.5f}'.format(forget)
    if not os.path.isdir(path_):
        os.mkdir(path_)

    if not os.path.exists(path_ + '/run.py'):
        text = writing_run(home_path,diagnostics_in_state=diagnostics_in_state,obs_paths=obs_paths,forget=forget,observations_z=observations_z,exp_obs=exp_obs,no_log=no_log)
        file_ = open(path_ + '/run.py','w')
        file_.write(text)
        file_.close()

    if not os.path.exists(path_ + '/jobParallelSlurm'):
        os.system('cp reference/jobParallelSlurm ' + path_ + '/')
    if not os.path.exists(path_ + '/bcs'):
        os.system('cp -r reference/bcs ' + path_ + '/')
    if not os.path.exists(path_ + '/gotm_0001.yaml'):
        for i in range(1,num_ensembles+1):
            os.system('cp gotms/gotm_{:04d}.yaml '.format(i) + path_ + '/')
    if not os.path.exists(path_ + '/fabm_0001.yaml'):
        for i in range(1,num_ensembles+1):
            os.system('cp fabms/fabm_{:04d}.yaml '.format(i) + path_ + '/')

    for i in range(1,num_ensembles+1):
        os.system('cp initializations/restart_{:04d}.nc '.format(i) + path_ + '/')

    os.system('cp '+path_+'/gotm_0001.yaml '+path_+'/gotm.yaml')
    os.system('cp '+path_+'/fabm_0001.yaml '+path_+'/fabm.yaml')
    os.system('cp '+path_+'/restart_0001.nc'+path_+'restart.nc')

def creating_all_work_spaces(home_path,da_path_,N_):
    
    da_path = da_path_ + '/da_chla_nap_cdom_assimilation'
    if not os.path.isdir(da_path):
        os.mkdir(da_path)
    diagnostics_in_state = ["total_chlorophyll","lightspectral_NAP","lightspectral_CDOM"]
    obs_paths = ['chla_inverted.txt','nap_inverted.txt','cdom_inverted.txt']
    observations_z=[-26,-26,-26]
    forgetin_factors = np.linspace(0.91,0.99,10)
    
    for forget in forgetin_factors:
        creating_work_space(home_path,da_path,diagnostics_in_state,obs_paths,observations_z,forget,num_ensembles=N_)

    
    da_path = da_path_ + '/da_chla_assimilation'
    if not os.path.isdir(da_path):
        os.mkdir(da_path)
    diagnostics_in_state = ["total_chlorophyll"]
    obs_paths = ['chla_inverted.txt']
    observations_z=[-26]
    
    for forget in forgetin_factors:
        creating_work_space(home_path,da_path,diagnostics_in_state,obs_paths,observations_z,forget,num_ensembles=N_)


        
    da_path = da_path_ + '/da_chla_buoy_assimilation'
    if not os.path.isdir(da_path):
        os.mkdir(da_path)
    diagnostics_in_state = ["total_chlorophyll"]
    obs_paths = ['chla_std.txt']

    for forget in forgetin_factors:
        creating_work_space(home_path,da_path,diagnostics_in_state,obs_paths,observations_z,forget,num_ensembles=N_)

    

    da_path = da_path_ + '/da_rrs_assimilation'
    if not os.path.isdir(da_path):
        os.mkdir(da_path)
    diagnostics_in_state = ['lightspectral_Rrs425','lightspectral_Rrs450','lightspectral_Rrs500','lightspectral_Rrs525','lightspectral_Rrs550']
    obs_paths = ['rrs_425.txt','rrs_450.txt','rrs_500.txt','rrs_525.txt','rrs_550.txt']
    observations_z=[-1,-1,-1,-1,-1]
    
    for forget in forgetin_factors:
        creating_work_space(home_path,da_path,diagnostics_in_state,obs_paths,observations_z,forget,num_ensembles=N_)

def test(da_path):
    diagnostics_in_state = ['lightspectral_Rrs425','lightspectral_Rrs450','lightspectral_Rrs500','lightspectral_Rrs525','lightspectral_Rrs550']
    obs_paths = ['rrs_425_no_log.txt','rrs_450_no_log.txt','rrs_500_no_log.txt','rrs_525_no_log.txt','rrs_550_no_log.txt']
    observations_z=[-1,-1,-1,-1,-1]
    forgetin_factors = [0.5       , 0.55444444, 0.60888889, 0.66333333, 0.71777778,
       0.77222222, 0.82666667, 0.88111111, 0.91      , 0.91888889, 0.92777778, 0.93666667, 0.94555556,\
           0.95444444, 0.96333333, 0.97222222, 0.98111111, 0.99,      ]

    
    for forget in forgetin_factors:
        creating_work_space(home_path,da_path,diagnostics_in_state,obs_paths,observations_z,forget,exp_obs=False)

def argument_parser():
    parser = argparse.ArgumentParser(
        prog='create_forgeting_factors_experiments',
        description='Create the folders and copy the data needed to run the ensemble data assimilation experiments',
        epilog='contact: carlos.soto362@gmail.com',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-hp','--home_path',help='Path with the folders: forcings, observations, fabms, gotms, initializations, reference and plugins',default='.',type=str)
    parser.add_argument('-dp','--assimilation_path',help='Path were to create the data assimilation experiments.',default='.',type=str)
    parser.add_argument('-N','--number_ensemble_members',help='Number of ensemble members to use for the simulation experiments.', default=2,type=int)
    
    
    return parser.parse_args()
        
if __name__ == "__main__":

    args = argument_parser()
    creating_all_work_spaces(args.home_path,args.assimilation_path,args.number_ensemble_members)



