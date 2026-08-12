import eatpy,sys,os,datetime,numpy
sys.path.append('/g100_work/OGS23_PRACE_IT/csoto/eat/tests/experiments/Ensemble_two/plugins')
import transform_clean as transform
import online_noise as noise

diagnostics_in_state = ['total_chlorophyll','lightspectral_NAP','lightspectral_CDOM','lightspectral_Rrs425','lightspectral_Rrs450','lightspectral_Rrs500','lightspectral_Rrs525','lightspectral_Rrs550']
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

experiment.run(filter)
    
