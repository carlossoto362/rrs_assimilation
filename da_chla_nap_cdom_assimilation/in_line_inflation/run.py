import eatpy,sys,os,datetime,numpy
sys.path.append('/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/plugins')
import transform_clean as transform
import online_noise as noise

diagnostics_in_state = ['total_chlorophyll','lightspectral_NAP','lightspectral_CDOM']
experiment = eatpy.models.GOTM(    diagnostics_in_state=diagnostics_in_state,
    start=datetime.datetime(2001, 1, 1), stop=datetime.datetime(2010, 12, 31)
)
filter = eatpy.PDAF(eatpy.pdaf.FilterType.ESTKF,forget=1)

bgc_variables = ['O4_n','Z6_p','R8_s','R6_n','Z4_p','B1_n','R6_p','Z6_n','O3_c','R1_p','R3_c','Z3_p','Z4_c','B1_c','R2_c','R1_c','Z5_n','O5_c','O2_o','Z6_c','Z5_c','B1_p','N6_r','O3h_h','Z5_p','R6_s','Z3_n','R8_n','Z3_c','R8_p','Z4_n','R1_n','N1_p','N3_n','N4_n','N5_s','R6_c','R8_c','X1_c','X2_c','X3_c','P1_c','P1_n','P1_p','P1_Chl','P1_s','P2_c','P2_n','P2_p','P2_Chl','P3_c','P3_n','P3_p','P3_Chl','P4_c','P4_n','P4_p','P4_Chl']
bgc_variables += diagnostics_in_state

experiment.add_plugin(
    eatpy.plugins.select.Select(include=bgc_variables)
)

experiment.add_plugin(
    transform.Log(
        *bgc_variables,
        transform_obs = False,
        minimum = 1e-9,
        log10 = False,
        max_nc = '/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/plugins/ncfile_ranges.nc',
        verbose = False,
    )
)

num_hours = int((datetime.datetime(2010, 12, 31) - datetime.datetime(2001, 1, 1)).days*6)
experiment.add_dummy_observations(numpy.array([datetime.datetime(2001,1,1)+datetime.timedelta(hours=int(4*i)) for i in range(1,num_hours)]))

experiment.add_plugin(
    noise.add_noise(
        path_C_squared = '/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/no_assimilation_statistics/square_cov.npy',
            diagnostics_in_state = diagnostics_in_state,
            method = 1,   #1 -> constant covariance matrix, 2 -> use covariance matrix of state, 3 -> use correlation matrix of state.
            rho = 0.26,
            gamma = 0.2,
            num_obs = 3,
            num_ensemble_members = 148,
            dump_noise_slide = [[588, 784], [784, 980], [980, 1176], [1176, 1372]], #phosphate (N1_p), nitrate (N3_n), 
                                                                                    #ammonium (N4_n),silicate (N5_s)
            delta_t=20,
            add_bias = False,
            add_R = False,
            verbose = True,
            max_rho = 1
        )
)

experiment.add_observations('total_chlorophyll[-26]', '/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/observation/chla_inverted.txt')
experiment.add_observations('lightspectral_NAP[-26]', '/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/observation/nap_inverted.txt')
experiment.add_observations('lightspectral_CDOM[-26]', '/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/observation/cdom_inverted.txt')
experiment.run(filter)
    
