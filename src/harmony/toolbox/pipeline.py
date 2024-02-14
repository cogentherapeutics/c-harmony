
from .constants import  RESULT_DIR, REFERENCE, COMPARISON, environment
import os, subprocess
import pandas as pd
import json 

from .query import (
        process_tcr_barcode_umi,
        clonotypes_frequency,
        get_files_harmony,
        get_top20_clonotypes,
        tcr_stitching_comparsion,
        gex_analysis,
        hit_analysis

)
from .utils import s3_download, s3_list, get_metadata, s3_file_exists, get_datatypes
from .aggregate import (
    
    load_df

)

def harmony(experiments):

    os.makedirs(f"tmp", exist_ok=True)
    os.makedirs(f"results", exist_ok=True)
    
    try:
        # Create the directory
        os.makedirs(f'results')
        print(f"Directory harmony_results created successfully.")
    except FileExistsError:
        print(f"Directory results already exists.")

    ######################################################################################
    #####Download metadata file for storing information of an experiment ##################
    ######################################################################################

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
        gex_rlist  = []
       

        try:
            os.makedirs(f'results/{experiment}')
        except:
            print(f'results/{experiment} already exists!')

        if s3_file_exists(f's3://captan/{COMPARISON}/{experiment}/metadata/{experiment}_samples.csv'):
            samples, reference = get_metadata(experiment, REFERENCE, COMPARISON)
            samples.sort()
            print (samples)

        stat = get_datatypes(experiment, REFERENCE)
        print ((stat))
        stat.to_csv(f'results/{experiment}/{experiment}_datatypes.csv',index=False )
        for sample in samples:
            summary = get_files_harmony(sample, reference, COMPARISON )
            file_summary.append(summary)

            if all(value is False for value in summary[1].values()):
                print (f"Check the {sample} has ran properly at {COMPARISON} and {REFERENCE}")
            else:
                print ("Found files ")

                # if (summary[1]['tcr-clonotypes']):
                #     # df_old = load_df(f'tmp/{experiment}/reference/{sample}__TCR_filtered_contig_annotations.csv')
                #     # df_new = load_df(f'tmp/{experiment}/comparison/{sample}__TCR_filtered_contig_annotations.csv')

                #     ######################################################################################
                #     #####Calling  functions to run tcr comparison ##################
                #     ######################################################################################


                #     data, df_alpha_u, df_beta_u, df_alpha_i, df_beta_i = process_tcr_barcode_umi(sample)
                #     r_pvals.append(data)
                #     df_alpha_u.to_csv(f'results/{experiment}/{sample}_alphas_union.csv')
                #     df_beta_u.to_csv(f'results/{experiment}/{sample}_betas_union.csv')
                #     df_alpha_i.to_csv(f'results/{experiment}/{sample}_alphas_intersection.csv')
                #     df_beta_i.to_csv(f'results/{experiment}/{sample}_betas_intersection.csv')

                #     clono_data, df_clono_outer, df_clono_inner = clonotypes_frequency(sample)
                #     r_pval_clono.append(clono_data)


                #     df_clono_outer.to_csv(f'results/{experiment}/{sample}_clonotypes_union.csv')
                #     df_clono_inner.to_csv(f'results/{experiment}/{sample}_clonotypes_intersection.csv')

                #     get_top20_clonotypes(sample).to_csv(f'results/{experiment}/{sample}_top20_clonotype_frequency.csv')

                #     tcrid_js =  tcr_stitching_comparsion(sample)
                #     js_list.append(tcrid_js)
                # else:
                #     pass

                # if (summary[1]['gex-analysis'] ):
                #     gex_rvalue = gex_analysis(sample, reference,COMPARISON)
                #     if  gex_rvalue:
                #         gex_rlist.append(gex_rvalue)
                # else: pass

        merge_count_sorted = hit_analysis(sample)   
        print (merge_count_sorted.head())
        merge_count_sorted.to_csv(f'results/{experiment}/{experiment}_hit_analysis_comparison.csv')   
        print ( merge_count_sorted.loc[merge_count_sorted['unique hits'] == 'both', 'count'].iloc[0]  )
        print (merge_count_sorted['unique hits'] == 'new')         
        # if any(value is True for value in summary[1].values()):
        #     s3_download(f'{RESULT_DIR}/{environment}/queue.csv', f'tmp/queue.csv')
        #     try:
        #         with open('tmp/queue.csv', 'r') as file:
        #             lines = [line.strip() for line in file.readlines()]
        #             print (lines)
        #     except FileNotFoundError:
        #         print ("queue.csv doesnot exists!")
        # # If the file doesn't exist, create it with the new item
        # if experiment not in lines:
        #     with open(f'tmp/queue.csv', 'a') as file:
        #         file.write(str(experiment)+'\n')
    

        # with open(f'results/{experiment}/{experiment}_sample_status.json', 'w') as file_json:
        #     json.dump(file_summary, file_json, indent=2)

        # with open(f'results/{experiment}/{experiment}_tcrid_jaccard_similarity.json', 'w') as file_json:
        #     json.dump(js_list, file_json, indent=2)
            
        # with open(f'results/{experiment}/{experiment}_gex_umi_rvalue.json', 'w') as file_json:
        #     json.dump(gex_rlist, file_json, indent=2)   

        # with open(f'results/{experiment}/{experiment}_tcr_clonotype_rvalue.json', 'w') as file_json:
        #     json.dump(r_pval_clono, file_json, indent=2)      

        # with open(f'results/{experiment}/{experiment}_tcr_barcode_umi_rvalue.json', 'w') as file_json:
        #     json.dump(r_pvals, file_json, indent=2)
        # subprocess.run(f"""
        #     echo aws s3 cp results/{experiment} {RESULT_DIR}/development/{experiment} --recursive 
        #     aws s3 cp results/{experiment} {RESULT_DIR}/development/{experiment} --recursive 
        #     aws s3 cp tmp/queue.csv {RESULT_DIR}/development/queue.csv

        # """, shell=True)
    return


