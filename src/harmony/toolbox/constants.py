import os

#RESULT_DIR = 's3://captan/haromony_results/'
METADATA = 'metadata'
RESULT_DIR = 'harmony_results'
COMPARISON = 'CR7_refdata7'
REFERENCE = 'experiments-v0.40'


RESULTS_DICT = {
                'tet-tenx': 'TET_probe_hydrogel_umi_counts.csv',
                'adt-tenx' : 'ADTTOTALSEQC_probe_hydrogel_umi_counts.csv',
                'merge' : 'MERGE_tcr_adt_with_sampled_empty_hydrogels_barcode_separated.csv', 
                'hash-demux' : '_MERGE_deconvoluted_only_singlets.csv',
                'hit-analysis': 'HITANALYSIS_hit_analysis_all_hits.csv',
                'tcr-clonotypes': 'TCR_all_observed_clonotypes.csv',
                'tcr-stitching' : 'TCR_Full_Length_Stitched_TCRs_With_IDs.csv',
                'gex-analysis': 'GEX_metrics_summary.csv'
}

CLONOTYPE_REF_HPV_CMV = {'CAMREDSLSGGYQKVTF;_CASSLLSRASYEQYF;':'Astarte_HPV',
                         'CILNNNNDMRF;CLPLQGGSNYKLTF;_CAWSISDLAKNIQYF;':'Astarte_CMV',
                         'CLPLQGGSNYKLTF;_CAWSISDLAKNIQYF;':'Astarte_CMV',
                         'CILNNNNDMRF;_CAWSISDLAKNIQYF;':'Astarte_CMV'}

# TODO: Remove CAASI?
CLONOTYPE_REF_MART1_CONTROL = {'CAVNNARLMF;_CASSEVTLGNYGYTF;':'Astarte_MART1',
                               'CAVNNARLMF;_CASSLAPTSGGELF;':'Astarte_MART1',
                               'CAVNNARLMF;CAGARAGGTSYGKLTF;_CASSLAPTSGGELF;':'Astarte_MART1',
                               'CAGARAGGTSYGKLTF;_CASSLAPTSGGELF;':'Astarte_MART1',
                               'CAVGGNNDMRF;CAGARAGGTSYGKLTF;_CASSLAPTSGGELF;':'Astarte_MART1',
                               'CAVGGNNDMRF;_CASSLAPTSGGELF;':'Astarte_MART1',
                               'CAVNTGGFKTIF;_CSVDPGGSHEQYF;':'Astarte_MART1',
                               'CASGNTPLVF;_CASSETGSSSYEQYF;':'Astarte_MART1',
                               'CAAGTGANNLFF;_CSASVGNQPQHF;':'Astarte_MART1',
                               'CAVGTGGFKTIF;_CASSRQGLGQPQHF;':'Astarte_MART1',
                               'CAASI;_CASSPLGQEAFF;':'Astarte_MART1',
                               'CAASIGFGNVLHC;_CASSPLGQEAFF;':'Astarte_MART1',
                               'CASGNTPLVF;_CASSEVTLGNYGYTF;':'Astarte_MART1',
                               'CAVNNARLMF;_CSVDPGGSHEQYF;':'Astarte_MART1',
                               'CSNYKLTF;_CASSMTSFADTYNEQFF;':'Astarte_MART1',
                               'CTCSNYKLTF;_CASSMTSFADTYNEQFF;':'Astarte_MART1'}

CHAIN_REF_HPV = {'alpha': 'CAMREDSLSGGYQKVTF', 'beta': 'CASSLLSRASYEQYF'}

CHAIN_REF_CMV = {'alpha1': 'CILNNNNDMRF', 'alpha2': 'CLPLQGGSNYKLTF', 'beta': 'CAWSISDLAKNIQYF'}

# TODO: Remove CAASI?
CHAIN_REF_MART1 = {'alphas': ['CAVNNARLMF', 'CAGARAGGTSYGKLTF', 'CAVGGNNDMRF', 'CAVNTGGFKTIF',
                             'CASGNTPLVF','CAAGTGANNLFF', 'CAVGTGGFKTIF', 'CAASI', 'CAASIGFGNVLHC',
                             'CASGNTPLVF', 'CAVNNARLMF', 'CSNYKLTF', 'CTCSNYKLTF'],
                   'betas': ['CASSLAPTSGGELF', 'CSVDPGGSHEQYF', 'CASSETGSSSYEQYF', 'CSASVGNQPQHF',
                            'CASSRQGLGQPQHF', 'CASSPLGQEAFF', 'CASSEVTLGNYGYTF', 'CSVDPGGSHEQYF',
                            'CASSMTSFADTYNEQFF']}

CONTROL_TET_LIST = ['CMV_WT','HPV-HEK'] # will show up in heatmaps with last at top, then second, etc...