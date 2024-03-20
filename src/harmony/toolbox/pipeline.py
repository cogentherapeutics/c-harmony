
from .constants import  RESULT_DIR, REFERENCE, COMPARISON, environment
import os, subprocess
import pandas as pd
import json, logging 
from scipy import stats

from .query import (
        process_tcr_barcode_umi,
        clonotypes_frequency,
        get_files_harmony,
        get_top20_clonotypes,
        tcr_stitching_comparsion,
        gex_analysis,
        hit_analysis

)
from .utils import (
    
        s3_download, 
        s3_list, 
        get_metadata, 
        s3_file_exists,
        get_datatypes

)
from .aggregate import (
    
    load_df,
    extract_betas,
    extract_alphas,
    contigs_to_clonotypes,
    load_df_clonotypes

)

def process_tcr_barcode_umi(sample):


    '''

    Scenario 1: Calculate for the detected barcode union from REFERENCE(Cell Ranger 3.1.0) and COMPARISON (Cell Ranger 7.1.0).
    union_r
    union_r_pval

    Scenario 2: Calculate for the detected barcode intersection between Cell Ranger 3.1.0 and Cell Ranger 7.1.0
    intersection_r
    intersection_r_pval


    Additionally we have the top 12 and top 25 detected clonotype proportions shared between Cell Ranger 3.1.0 and Cell Ranger 7.1.0 results.
    t12
    t25

    The scatterplots have been colour coded so that blue points are productive hydrogels whose C gene is TRAC and red points are productive hydrogels whose C genes are TRBC1 or TRBC2.

    '''

    experiment = sample.split('_')[0]

    try:
        df_old = load_df(f'tmp/{experiment}/reference/{sample}__TCR_filtered_contig_annotations.csv')
        df_new = load_df(f'tmp/{experiment}/comparison/{sample}__TCR_filtered_contig_annotations.csv')

        df_betas_union = pd.merge(
            extract_betas(df_old)[['barcode', 'umis']].rename(columns={'umis': 'x'}),
            extract_betas(df_new)[['barcode', 'umis']].rename(columns={'umis': 'y'}),
            on='barcode',
            how='outer'
        ).fillna(0)
        df_alphas_union = pd.merge(
            extract_alphas(df_old)[['barcode', 'umis']].rename(columns={'umis': 'x'}),
            extract_alphas(df_new)[['barcode', 'umis']].rename(columns={'umis': 'y'}),
            on='barcode',
            how='outer'
        ).fillna(0)
        union_r, union_r_pval = stats.pearsonr(pd.concat([df_betas_union.x, df_alphas_union.x]),
                                        pd.concat([df_betas_union.y, df_alphas_union.y]))

        #print (union_r,union_r_pval)


        df_betas_intersection = pd.merge(
            extract_betas(df_old)[['barcode', 'umis']].rename(columns={'umis': 'x'}),
            extract_betas(df_new)[['barcode', 'umis']].rename(columns={'umis': 'y'}),
            on='barcode',
            how='inner'
        )
        
        df_alphas_intersection = pd.merge(
            extract_alphas(df_old)[['barcode', 'umis']].rename(columns={'umis': 'x'}),
            extract_alphas(df_new)[['barcode', 'umis']].rename(columns={'umis': 'y'}),
            on='barcode',
            how='inner'
        )

        intersection_r, intersection_r_pval = stats.pearsonr(pd.concat([df_betas_intersection.x, df_alphas_intersection.x]),
                                                            pd.concat([df_betas_intersection.y, df_alphas_intersection.y]))

        old_clonotypes = contigs_to_clonotypes(df_old, sample)
        old_12 = old_clonotypes.iloc[:12].clonotype_label.tolist()
        old_25 = old_clonotypes.iloc[:25].clonotype_label.tolist()
        
        new_clonotypes = contigs_to_clonotypes(df_new, sample)
        new_12 = new_clonotypes.iloc[:12].clonotype_label.tolist()
        new_25 = new_clonotypes.iloc[:25].clonotype_label.tolist()
        #r_pvals.append

        return ([sample, {'union_r': union_r,
                                'union_r_pval': union_r_pval,
                                'intersection_r': intersection_r,
                                'intersection_r_pval': intersection_r_pval,
                                't12': len(set(old_12).intersection(set(new_12)))/len(set(old_12)),
                                't25': len(set(old_25).intersection(set(new_25)))/len(set(old_25))
                                }]), df_alphas_union, df_betas_union, df_alphas_intersection, df_betas_intersection
    except:
        print (f"Contig annotations files not found for {sample}")


def clonotypes_frequency(sample):
    experiment =sample.split('_')[0]
    # oldfn = f'tmp/{experiment}/reference/{sample}__TCR_clonotypes.csv'
    # newfn = f'tmp/{experiment}/comparison/{sample}__TCR_clonotypes.csv'

    # s3_download(f's3:/{oldfn}', f'{REFERENCE}/{sample}__TCR_clonotypes.csv')
    # s3_download(f's3:/{newfn}', f'{COMPARISON}/{sample}__TCR_clonotypes.csv')
    try:

        df_old_clonotypes = load_df_clonotypes(f'tmp/{experiment}/reference/{sample}__TCR_clonotypes.csv')[['cdr3s_aa', 'frequency']].rename(columns={'frequency': 'x'})
        df_new_clonotypes = load_df_clonotypes(f'tmp/{experiment}/comparison/{sample}__TCR_clonotypes.csv')[['cdr3s_aa', 'frequency']].rename(columns={'frequency': 'y'})
        
        df_inner = pd.merge(df_old_clonotypes, df_new_clonotypes, on='cdr3s_aa', how='inner')
        df_inner['rank_x'] = df_inner['x'].rank(ascending=False, na_option='bottom')
        df_inner['rank_y'] = df_inner['y'].rank(ascending=False, na_option='bottom')
        
        df_outer = pd.merge(df_old_clonotypes, df_new_clonotypes, on='cdr3s_aa', how='outer')
        df_outer['rank_x'] = df_outer['x'].rank(ascending=False, na_option='bottom')
        df_outer['rank_y'] = df_outer['y'].rank(ascending=False, na_option='bottom')

        
        union_r, union_r_pval = stats.pearsonr(df_outer.fillna(0).x, df_outer.fillna(0).y)
        union_rho, union_rho_pval = stats.spearmanr(df_outer.rank_x, df_outer.rank_y)
        
        intersection_r, intersection_r_pval = stats.pearsonr(df_inner.x, df_inner.y)
        intersection_rho, intersection_rho_pval = stats.spearmanr(df_inner.rank_x, df_inner.rank_y)


        df_outer = pd.merge(df_old_clonotypes, df_new_clonotypes,
                            on='cdr3s_aa', how='outer').fillna(0)
        
        df_inner = pd.merge(df_old_clonotypes, df_new_clonotypes,
                            on='cdr3s_aa', how='inner')
            
        return ( ([sample, {'union_r': union_r,
                                'union_r_pval': union_r_pval,
                                'intersection_r': intersection_r,
                                'intersection_r_pval': intersection_r_pval,
                                'union_rho': union_rho,
                                'union_rho_pval': union_rho_pval,
                                'intersection_rho': intersection_rho,
                                'intersection_rho_pval': intersection_rho_pval
                            }]), df_outer, df_inner)
    except:
        print (f"TCR clonotypes files not found for {sample}")
        pass




def orchestrate_pipeline(
        
    harmony_log_path,
    error_log_path,
    reference,
    comparison,
    experiment
):

    captan_logger = logging.getLogger("captan")
    info_logger = logging.getLogger("information")
    error_logger = logging.getLogger("errors")

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

    stat.to_csv(f'results/{experiment}/{experiment}_datatypes.csv',index=False )
        
    for sample in samples:
        summary = get_files_harmony(sample, reference, COMPARISON )
        file_summary.append(summary)

        if all(value is False for value in summary[1].values()):
            error_logger.error (f"Check the {sample} has ran properly at {COMPARISON} and {REFERENCE}")
        else:
            print ("Found files ")

            if (summary[1]['tcr-clonotypes']):

                ######################################################################################
                #####Calling  functions to run tcr comparison ##################
                ######################################################################################


                data, df_alpha_u, df_beta_u, df_alpha_i, df_beta_i = process_tcr_barcode_umi(sample)
                r_pvals.append(data)
                df_alpha_u.to_csv(f'results/{experiment}/{sample}_alphas_union.csv')
                df_beta_u.to_csv(f'results/{experiment}/{sample}_betas_union.csv')
                df_alpha_i.to_csv(f'results/{experiment}/{sample}_alphas_intersection.csv')
                df_beta_i.to_csv(f'results/{experiment}/{sample}_betas_intersection.csv')

                clono_data, df_clono_outer, df_clono_inner = clonotypes_frequency(sample)
                r_pval_clono.append(clono_data)


                df_clono_outer.to_csv(f'results/{experiment}/{sample}_clonotypes_union.csv')
                df_clono_inner.to_csv(f'results/{experiment}/{sample}_clonotypes_intersection.csv')

                get_top20_clonotypes(sample).to_csv(f'results/{experiment}/{sample}_top20_clonotype_frequency.csv')

                tcrid_js =  tcr_stitching_comparsion(sample)
                js_list.append(tcrid_js)
            else:
                pass

            if (summary[1]['gex-analysis'] ):
                gex_rvalue = gex_analysis(sample, reference,COMPARISON)
                if  gex_rvalue:
                    gex_rlist.append(gex_rvalue)
            else: pass

    merge_count_sorted = hit_analysis(sample)   
    print (merge_count_sorted.head())
    merge_count_sorted.to_csv(f'results/{experiment}/{experiment}_hit_analysis_comparison.csv')   
    print ( merge_count_sorted.loc[merge_count_sorted['unique hits'] == 'both', 'count'].iloc[0]  )
    print (merge_count_sorted['unique hits'] == 'new')         
    if any(value is True for value in summary[1].values()):
        s3_download(f'{RESULT_DIR}/{environment}/queue.csv', f'tmp/queue.csv')
        try:
            with open('tmp/queue.csv', 'r') as file:
                lines = [line.strip() for line in file.readlines()]
                print (lines)
        except FileNotFoundError:
            print ("queue.csv doesnot exists!")
    # If the file doesn't exist, create it with the new item
    if experiment not in lines:
        with open(f'tmp/queue.csv', 'a') as file:
            file.write(str(experiment)+'\n')
    

    with open(f'results/{experiment}/{experiment}_sample_status.json', 'w') as file_json:
        json.dump(file_summary, file_json, indent=2)

    with open(f'results/{experiment}/{experiment}_tcrid_jaccard_similarity.json', 'w') as file_json:
        json.dump(js_list, file_json, indent=2)
        
    with open(f'results/{experiment}/{experiment}_gex_umi_rvalue.json', 'w') as file_json:
        json.dump(gex_rlist, file_json, indent=2)   

    with open(f'results/{experiment}/{experiment}_tcr_clonotype_rvalue.json', 'w') as file_json:
        json.dump(r_pval_clono, file_json, indent=2)      

    with open(f'results/{experiment}/{experiment}_tcr_barcode_umi_rvalue.json', 'w') as file_json:
        json.dump(r_pvals, file_json, indent=2)
    subprocess.run(f"""
        echo aws s3 cp results/{experiment} {RESULT_DIR}/development/{experiment} --recursive 
        aws s3 cp results/{experiment} {RESULT_DIR}/development/{experiment} --recursive 
        aws s3 cp tmp/queue.csv {RESULT_DIR}/development/queue.csv

    """, shell=True)
    return


