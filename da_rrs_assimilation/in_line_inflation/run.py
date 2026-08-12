import eatpy,sys,os,datetime,numpy
sys.path.append('/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/plugins')
import transform_clean as transform
import online_noise as noise

diagnostics_in_state = ['lightspectral_Rrs425','lightspectral_Rrs450','lightspectral_Rrs500','lightspectral_Rrs525','lightspectral_Rrs550']
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
            rho = 0.4, #change from 1 to 2, because it was increasing too much
            gamma = 0.1, #0.05 was better than 0.1, but i see is increasing progresibly. gets down too slow, i go back to 0.1, but then i add a maximum value for rho of 5.?? 
            num_obs = 5,
            num_ensemble_members = 148,
            dump_noise_slide = [[5, 201], [397, 593], [593, 789]], #phosphate (N1_p), 
                                                                             #ammonium (N4_n),silicate (N5_s)
            delta_t=10,
            add_bias = False,
            add_R = False,
            verbose = True,
            max_rho = 1
        )
)

experiment.add_observations('lightspectral_Rrs425[-1]', '/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/observation/rrs_425.txt')
experiment.add_observations('lightspectral_Rrs450[-1]', '/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/observation/rrs_450.txt')
experiment.add_observations('lightspectral_Rrs500[-1]', '/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/observation/rrs_500.txt')
experiment.add_observations('lightspectral_Rrs525[-1]', '/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/observation/rrs_525.txt')
experiment.add_observations('lightspectral_Rrs550[-1]', '/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/observation/rrs_550.txt')
experiment.run(filter)
    
