from math import ceil
from tabulate import tabulate

import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from itertools import chain

from .constants import RESULT_DIR, RESULTS_DICT,COMPARISON, REFERENCE
from .utils import (
     get_metadata,
     s3_file_exists, 
     s3_download, 
     file_sanity_check, 


)
from .aggregate import (
                        _agg_cdr3,
                        _label_clonotype, 
                        load_df, 
                        contigs_to_clonotypes, 
                        extract_alphas, 
                        extract_betas, 
                        load_df_clonotypes,
                        similar,
                        find_similarities,
                        remove_unpaired,
                        calculate_jaccard_similarity,
                        make_clonotypes_from_tcr,
                        calculate_cellranger_gex_umi_correlation_comparison
                        


)


def get_files_harmony(sample,r1,r2 ):
    experiment = sample.split('_')[0]
    '''
    Historically, it has found that we missed to catch the incomplete generation of results files that happens due to some unknown aws challenge to laucnh the nextflow/memory issues etc. 
    This block of code is to see all necessary files are generated in REFERENCE and COMPARISON before we start do actual results comparsion. 
    TODO: may be later can replce with a better logic.
    

    '''
    ###Tet-tenx files((:
    tet, reference, comparison = file_sanity_check(r1, r2,sample,'tet-tenx')
    adt , reference, comparison= file_sanity_check(r1, r2, sample,'adt-tenx')
    merge, reference, comparison = file_sanity_check(r1, r2, sample,'merge')
    hash, reference, comparison = file_sanity_check(r1, r2, sample,'hash-demux')
    hit, reference, comparison = file_sanity_check(r1, r2, sample,'hit-analysis')
    tcr_clonotype, reference, comparison = file_sanity_check(r1, r2, sample,'tcr-clonotypes')
    tcr_stitching, reference, comparison = file_sanity_check(r1, r2, sample,'tcr-stitching')
    gex_analysis, reference, comparison = file_sanity_check(r1, r2, sample,'gex-analysis')


    if tcr_clonotype:
        s3_download(
            f's3://captan/{reference}/{experiment}/preprocessing/tcr-tenx/{sample}/{sample}__TCR_cellranger_vdj/{sample}__TCR_filtered_contig_annotations.csv', f'tmp/{experiment}/reference/{sample}__TCR_filtered_contig_annotations.csv'
        )
        s3_download(
            f's3://captan/{comparison}/{experiment}/preprocessing/tcr-tenx/{sample}/{sample}__TCR_cellranger_vdj/{sample}__TCR_filtered_contig_annotations.csv', f'tmp/{experiment}/comparison/{sample}__TCR_filtered_contig_annotations.csv'
        )
        s3_download(

            f's3://captan/{reference}/{experiment}/preprocessing/tcr-tenx/{sample}/{sample}__TCR_cellranger_vdj/{sample}__TCR_clonotypes.csv', f'tmp/{experiment}/reference/{sample}__TCR_clonotypes.csv'
        )
        s3_download(

            f's3://captan/{comparison}/{experiment}/preprocessing/tcr-tenx/{sample}/{sample}__TCR_cellranger_vdj/{sample}__TCR_clonotypes.csv', f'tmp/{experiment}/comparison/{sample}__TCR_clonotypes.csv'
        )
        s3_download (

            f's3://captan/{reference}/{experiment}/preprocessing/tcr-stitching/{sample}/{sample}__TCR_Full_Length_Stitched_TCRs_With_IDs.csv', f'tmp/{experiment}/reference/{sample}__TCR_Full_Length_Stitched_TCRs_With_IDs.csv'
        )
        s3_download (

            f's3://captan/{comparison}/{experiment}/preprocessing/tcr-stitching/{sample}/{sample}__TCR_Full_Length_Stitched_TCRs_With_IDs.csv', f'tmp/{experiment}/comparison/{sample}__TCR_Full_Length_Stitched_TCRs_With_IDs.csv'
        )
        if gex_analysis:
            s3_download(

                f's3://captan/{reference}/{experiment}/preprocessing/gex-tenx/{sample}/{sample}__GEX_cellranger_count/{sample}__GEX_metrics_summary.csv', f'tmp/{experiment}/reference/{sample}__GEX_metrics_summary.csv'

            )
            s3_download(

                f's3://captan/{comparison}/{experiment}/preprocessing/gex-tenx/{sample}/{sample}__GEX_cellranger_count/{sample}__GEX_metrics_summary.csv', f'tmp/{experiment}/comparison/{sample}__GEX_metrics_summary.csv'

            )
        if hit:

            s3_download(

                f's3://captan/{reference}/{experiment}/preprocessing/hit-analysis-experiment-wide/{experiment}__HITANALYSIS_hit_analysis_hits.csv', f'tmp/{experiment}/reference/{experiment}__HITANALYSIS_hit_analysis_hits.csv'

            )
            s3_download(

                f's3://captan/{comparison}/{experiment}/preprocessing/hit-analysis-experiment-wide/{experiment}__HITANALYSIS_hit_analysis_hits.csv', f'tmp/{experiment}/comparison/{experiment}__HITANALYSIS_hit_analysis_hits.csv'

            )
    
    return ([sample, {'tet-tenx': tet,
                            'adt-tenx': adt,
                            'hit-analysis': hit,
                            'hash-demux': hash,
                            'merge': merge,
                            'tcr-clonotypes': tcr_clonotype,
                            'tcr-stitching': tcr_stitching,
                            'gex-analysis': gex_analysis
                            }])
    

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




'''
We are examining effects on detected clonotypes and their frequencies.

Pearson R correlation and Spearman Rho correlations are calculated via the following ways:

Scenario 1: Calculate for the detected clonotype union from Cell Ranger 3.1.0 and Cell Ranger 7.1.0.

union_r
union_r_pval
union_rho
union_rho_pval

Scenario 2: Calculate for the detected clonotype intersection between Cell Ranger 3.1.0 and Cell Ranger 7.1.0

intersection_r
intersection_r_pval
intersection_rho
intersection_rho_pval

Also calculated:

precision: Percentage Cell Ranger 7.1.0 clonotypes that are found in Cell Ranger 3.1.0 clonotypes.

recall: Percentage Cell Ranger 3.1.0 clonotypes that were found by Cell Ranger 7.1.0.

loose_precision: Relax constraints for considering two clonotypes the same. If they have matching numbers for TRAs and TRBs and each TRA or TRB is an equal or extension to the other's sequence then they will be considered the same clonotype.

loose_recall: Relax constraints for considering two clonotypes the same. If they have matching numbers for TRAs and TRBs and each TRA or TRB is an equal or extension to the other's sequence then they will be considered the same clonotype.

Following the loose_precision and loose_recall analysis are the clonotypes that are considered false negatives or false positives and which clonotypes they were matched with in the relaxed constraint.

Loose metric explanations:

Suppose that the clonotypes by version found are:
    Cell Ranger 3.1.0: A, B, D
    Cell Ranger 7.1.0: A', B, C

where:

    equal(A, A') -> False
    similar(A, A') -> True

then under a string definition we have

    precision: len({A', B, C}.intersection({A, B, D})) / len({A', B, C}) --> len({B})/len({A', B, C}) = 1 / 3
    recall: len({A', B, C}.intersection({A, B, D})) / len({A, B, D}) --> len({B}) / len({A, B, D}) = 1 / 3

yet by allowing similar(A, A') so that A' can be treated as finding A we now have after replacing A' with A:

    precisions: len({A, B, C}.intersection({A, B, D})) / len({A, B, C}) --> len({A, B}) / len({A, B, C}) = 2 / 3
    recall: len({A, B, C}.intersection({A, B, D})) / len({A, B, D}) --> len({A, B}) / len({A, B, D}) = 2 / 3

For the precision case A' would be a false positive as it seems like a new clonotype found by Cell Ranger 7.1.0 which
differs from the clonotypes found by Cell Ranger 3.1.0 and each new clonotype reduces the precision value.

For the recall case A' would be a false negative as it seems like a clonotype failed to be found by Cell Ranger 3.1.0 which
Cell Ranger 7.1.0 found and each clonotype failed to be found by Cell Ranger 3.1.0 reduces the recall value.

'''
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



def get_top20_clonotypes(sample):
    experiment =sample.split('_')[0]

    try:
        df_old_clonotypes = remove_unpaired(load_df_clonotypes(f'tmp/{experiment}/reference/{sample}__TCR_clonotypes.csv')[['cdr3s_aa', 'frequency']])
        df_new_clonotypes = remove_unpaired(load_df_clonotypes(f'tmp/{experiment}/comparison/{sample}__TCR_clonotypes.csv')[['cdr3s_aa', 'frequency']])

        top_20_df1 = df_old_clonotypes.sort_values(by='frequency', ascending=False).head(20)
        return (pd.merge(top_20_df1, df_new_clonotypes, 
                        how ='left', on = 'cdr3s_aa')[['cdr3s_aa','frequency_x','frequency_y']].fillna(0))
    except:
        print (f"TCR clonotypes files not found for {sample}")


def  tcr_stitching_comparsion(sample):
    experiment =sample.split('_')[0]
    try:

        tcr_set1 = pd.read_csv(f'tmp/{experiment}/reference/{sample}__TCR_Full_Length_Stitched_TCRs_With_IDs.csv', comment = '#')
        tcr_set2 = pd.read_csv(f'tmp/{experiment}/comparison/{sample}__TCR_Full_Length_Stitched_TCRs_With_IDs.csv', comment = '#')

        tcr_js = calculate_jaccard_similarity(set(tcr_set1['tcr_id']),set(tcr_set2['tcr_id']))
        clonotype_js = calculate_jaccard_similarity(set(make_clonotypes_from_tcr(tcr_set1)['clonotype']), set(make_clonotypes_from_tcr(tcr_set2)['clonotype']))

        return [sample , {'tcrid_js': tcr_js,'clonotype_js': clonotype_js}], 
    except:

        print (f"TCR stitching files not found for {sample}")
        pass

def hit_analysis(sample):

    '''
    We are examining the difference in hits identified between two cipher runs.Hits present in unique runs and both , will be taken based on "clonotype",
    epitope, experiment and sample. 

    TODO: We may extend later to see the diff in HTOS found in hts from both runs. 
    
    '''
    data = {'No: of samples with more hits in CR7':[0], 'No: of samples with more hits in CR3':[0]}
    more_hits_metric = pd.DataFrame(data)
    recall_dict = []
    precision_dict = []
    experiment =sample.split('_')[0]
    
    try:
        hit_old = pd.read_csv(f'tmp/{experiment}/reference/{experiment}__HITANALYSIS_hit_analysis_hits.csv')
        hit_new = pd.read_csv(f'tmp/{experiment}/comparison/{experiment}__HITANALYSIS_hit_analysis_hits.csv')
        if sorted(hit_old['sample'].unique().tolist()) == sorted(hit_new['sample'].unique().tolist()):
            print ("inside hit anaysis")
            if 'HTO' not in hit_old.columns:
            
                merged = pd.merge(
                    hit_old[['clonotype', 'experiment', 'sample','antigen','epitope', 'rating', 'reject']], 
                    hit_new[['clonotype', 'experiment', 'sample', 'antigen','epitope', 'rating', 'reject']], 
                    left_on=['clonotype', 'epitope', 'experiment', 'sample'],
                    right_on=['clonotype', 'epitope', 'experiment', 'sample'],
                    how='outer',
                    suffixes=('_new','_old'),
                    #suffixes=('_v0.40_old', '_v0.40'),
                    indicator=True
                )
            else:
        
                merged = pd.merge(
                    hit_old[['clonotype', 'HTO', 'experiment', 'sample','antigen','epitope', 'rating', 'reject']], 
                    hit_new[['clonotype',  'HTO','experiment', 'sample', 'antigen','epitope', 'rating', 'reject']], 
                    left_on=['clonotype', 'epitope', 'experiment', 'sample'],
                    right_on=['clonotype', 'epitope', 'experiment', 'sample'],
                    how='outer',
                    suffixes=('_new','_old'),
                    #suffixes=('_v0.40_old', '_v0.40'),
                    indicator=True
                )


            merged['_merge'] = merged['_merge'].map({'left_only': 'old', 'right_only': 'new', 'both': 'both'})
            merge_count =  merged['_merge'].value_counts().reset_index().rename(columns={'index': 'version', '_merge': 'unique hits'})
            
    #         #merge_count_sorted = merge_count.sort_values(by='unique hits', ascending=False).reset_index()
            

    #         # if merge_count_sorted.at[1, 'unique hits'] > merge_count_sorted.at[2, 'unique hits'] :
    #         #     more_hits_metric['No: of samples with more hits in new'] += 1
    #         # else:
    #         #     more_hits_metric['No: of samples with more hits in old'] += 1 


    #     '''
    #     TODO: Number of more hits in CR7, precision and recall to be done
    #     '''

    # ###Get top quality hits
    #     top_new = hit_new[hit_new.rating >= 4]
    #     top_old = hit_old[hit_old.rating >= 4]
        
    #     for sample in hit_new['sample'].unique().tolist():
    #         new_sample_top = top_new[top_new['sample'] == sample].sort_values(by='rating', ascending=False)
    #         old_sample_top = top_old[top_old['sample'] == sample].sort_values(by='rating', ascending=False)
    #         new_sample_top.to_csv(f'{RESULT_DIR}/{experiment}/{sample}_top_hits_new.csv')
    #         old_sample_top.to_csv(f'{RESULT_DIR}/{experiment}/{sample}_top_hits_old.csv')

    #     return merged
        return merge_count
    except:
        print (f"Hit files not found for {experiment}")

def gex_analysis(sample, reference, comparison):
    experiment =sample.split('_')[0]
    print ("inside gex anaysis")

    gex_df = calculate_cellranger_gex_umi_correlation_comparison(reference, comparison , sample, experiment)
    print ([sample,gex_df])
    return ([sample, gex_df])