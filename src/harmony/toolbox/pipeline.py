
from .constants import  RESULT_DIR, REFERENCE, COMPARISON
import os

from .query import (
        process_tcr_barcode_umi,
        clonotypes_frequency,
        get_files_harmony,
        get_top20_clonotypes,
        tcr_stitching_comparsion

)
from .utils import s3_download, s3_list, get_metadata, s3_file_exists
from .aggregate import (
    
    load_df

)

def harmony(experiments):

    os.makedirs(f"tmp", exist_ok=True)
    
    try:
        # Create the directory
        os.makedirs(f'{RESULT_DIR}')
        print(f"Directory harmony_results created successfully.")
    except FileExistsError:
        print(f"Directory {RESULT_DIR} already exists.")

    try: 
        os.makedirs(f'tmp/metadata')
        
    except:
         print(f"Directory 'tmp/metadata already exists.")
    for experiment in experiments:
        #os.makedirs(f"temp/{experiment}", exist_ok=True)
        r_pvals = []
        r_pval_clono = []
        file_summary = []
        js_list = []
       
        try:
            os.makedirs(f'{RESULT_DIR}/{experiment}')
        except:
            print(f'{RESULT_DIR}/{experiment} already exists!')

        if s3_file_exists(f's3://captan/{COMPARISON}/{experiment}/metadata/{experiment}_samples.csv'):
            samples, reference = get_metadata(experiment, REFERENCE, COMPARISON)
            samples.sort()

        for sample in samples:

            summary = get_files_harmony(sample, reference, COMPARISON )
            file_summary.append(summary)
            
            if (summary[1]['tcr-clonotypes']):
                df_old = load_df(f'tmp/{experiment}/reference/{sample}__TCR_filtered_contig_annotations.csv')
                df_new = load_df(f'tmp/{experiment}/comparison/{sample}__TCR_filtered_contig_annotations.csv')
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

                tcrid_js =  tcr_stitching_comparsion(sample)
                js_list.append(tcrid_js)
            

        with open(f'{RESULT_DIR}/{experiment}/{experiment}_tcr_barcode_umi_rvalue.txt', 'w') as file:
            for item in r_pvals:
                file.write(str(item)+'\n')
        file.close()
        with open(f'{RESULT_DIR}/{experiment}/{experiment}_tcr_clonotype_rvalue.txt', 'w') as file:
            for item in r_pval_clono:
                file.write(str(item)+'\n')
        file.close()

        with open(f'{RESULT_DIR}/{experiment}/{experiment}_sample_status.txt', 'w') as file:
            for item in file_summary:
                file .write(str(item)+'\n')
        file.close()
        with open(f'{RESULT_DIR}/{experiment}/{experiment}_tcrid_jaccard_similarity.txt', 'w') as file:
            for item in  js_list:
                file.write(str(item)+'\n')
        file.close()

    return


