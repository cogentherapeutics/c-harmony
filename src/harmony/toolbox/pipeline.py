
from .constants import METADATA, RESULT_DIR, REFERENCE, COMPARISON
import os

from .query import (
        process_tcr_barcode_umi,
        clonotypes_frequency,
        get_files_harmony,
        get_top20_clonotypes

)
from .utils import s3_download, s3_list, get_metadata, s3_file_exists
from .aggregate import load_df

def harmony(experiments):
    
    try:
        # Create the directory
        os.makedirs(f'{RESULT_DIR}')
        print(f"Directory harmony_results created successfully.")
    except FileExistsError:
        print(f"Directory {RESULT_DIR} already exists.")

    try: 
        os.makedirs(f'{METADATA}')
        
    except:
         print(f"Directory {METADATA} already exists.")
    for experiment in experiments:
        
        r_pvals = []
        r_pval_clono = []
        file_summary = []
        try:
            os.makedirs(f'{RESULT_DIR}/{experiment}')
        except:
            print(f'{RESULT_DIR}/{experiment} already exists!')

        if s3_file_exists(f's3://captan/{COMPARISON}/{experiment}/metadata/{experiment}_samples.csv'):
            samples = get_metadata(experiment)
            samples.sort()

        for sample in samples:
            summary = get_files_harmony(sample)
            file_summary.append(summary)

            if (summary[1]['tcr-clonotypes']):
                df_old = load_df(f'{REFERENCE}/{sample}__TCR_filtered_contig_annotations.csv')
                df_new = load_df(f'{COMPARISON}/{sample}__TCR_filtered_contig_annotations.csv')
                data, df_alpha_u, df_beta_u, df_alpha_i, df_beta_i = process_tcr_barcode_umi(sample, df_old, df_new)
                r_pvals.append(data)
                df_alpha_u.to_csv(f'{RESULT_DIR}/{experiment}/{sample}_alphas_union.csv')
                df_beta_u.to_csv(f'{RESULT_DIR}/{experiment}/{sample}_betas_union.csv')
                df_alpha_i.to_csv(f'{RESULT_DIR}/{experiment}/{sample}_alphas_intersection.csv')
                df_beta_i.to_csv(f'{RESULT_DIR}/{experiment}/{sample}_betas_intersection.csv')

                clono_data, df_clono_outer, df_clono_inner = clonotypes_frequency(sample)
                r_pval_clono.append(clono_data)
                df_clono_outer.to_csv(f'{RESULT_DIR}/{experiment}/{sample}_clonotypes_union.csv')
                df_clono_inner.to_csv(f'{RESULT_DIR}/{experiment}/{sample}_clonotypes_intersection.csv')

                get_top20_clonotypes(sample).to_csv(f'{RESULT_DIR}/{experiment}/{sample}_top20_clonotype_frequency.csv')
                

    
    with open(f'{RESULT_DIR}/{experiment}/{experiment}_tcr_barcode_umi_rvalue.txt', 'w') as file:
        for item in r_pvals:
            file.write(str(item)+'\n')
    with open(f'{RESULT_DIR}/{experiment}/{experiment}_tcr_clonotype_rvalue.txt', 'w') as file:
        for item in r_pval_clono:
            file.write(str(item)+'\n')


    return


