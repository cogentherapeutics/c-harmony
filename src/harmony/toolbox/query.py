from math import ceil
from tabulate import tabulate

import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from itertools import chain

from .constants import RESULT_DIR, METADATA, RESULTS_DICT,COMPARISON, REFERENCE
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
                        remove_unpaired


)


def get_files_harmony(sample):
    experiment = sample.split('_')[0]
    print (sample)
    '''
    Historically, it has found that we missed to catch the incomplete generation of results files that happens due to some unknown aws challenge to laucnh the nextflow/memory issues etc. 
    This block of code is to see all necessary files are generated in REFERENCE and COMPARISON before we start do actual results comparsion. 
    TODO: may be later can replce with a better logic.
    

    '''
    ###Tet-tenx files((:
    tet = file_sanity_check(COMPARISON, REFERENCE, sample,'tet-tenx')
    adt = file_sanity_check(COMPARISON, REFERENCE, sample,'adt-tenx')
    merge = file_sanity_check(COMPARISON, REFERENCE, sample,'merge')
    hash = file_sanity_check(COMPARISON, REFERENCE, sample,'hash-demux')
    hit = file_sanity_check(COMPARISON, REFERENCE, sample,'hit-analysis')
    tcr_clonotype = file_sanity_check(COMPARISON, REFERENCE, sample,'tcr-clonotypes')
    tcr_stitching = file_sanity_check(COMPARISON, REFERENCE, sample,'tcr-stitching')
    gex_analysis = file_sanity_check(COMPARISON, REFERENCE, sample,'gex-analysis')
    


    
    return ([sample, {'tet-tenx': tet,
                            'adt-tenx': adt,
                            'hit-analysis': hit,
                            'hash-demux': hash,
                            'merge': merge,
                            'tcr-clonotypes': tcr_clonotype,
                            'tcr-stitching': tcr_stitching,
                            'gex-analysis': gex_analysis
                            }])
    

def process_tcr_barcode_umi(sample, df_old, df_new):


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
    oldfn = f'/captan/{REFERENCE}/{experiment}/preprocessing/tcr-tenx/{sample}/{sample}__TCR_cellranger_vdj/{sample}__TCR_clonotypes.csv'
    newfn = f'/captan/{COMPARISON}/{experiment}/preprocessing/tcr-tenx/{sample}/{sample}__TCR_cellranger_vdj/{sample}__TCR_clonotypes.csv'

    s3_download(f's3:/{oldfn}', f'{REFERENCE}/{sample}__TCR_clonotypes.csv')
    s3_download(f's3:/{newfn}', f'{COMPARISON}/{sample}__TCR_clonotypes.csv')

    df_old_clonotypes = load_df_clonotypes(f'{REFERENCE}/{sample}__TCR_clonotypes.csv')[['cdr3s_aa', 'frequency']].rename(columns={'frequency': 'x'})
    df_new_clonotypes = load_df_clonotypes(f'{COMPARISON}/{sample}__TCR_clonotypes.csv')[['cdr3s_aa', 'frequency']].rename(columns={'frequency': 'y'})
    
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



def get_top20_clonotypes(sample):
    experiment =sample.split('_')[0]
    
    df_old_clonotypes = remove_unpaired(load_df_clonotypes(f'{REFERENCE}/{sample}__TCR_clonotypes.csv')[['cdr3s_aa', 'frequency']])
    df_new_clonotypes = remove_unpaired(load_df_clonotypes(f'{COMPARISON}/{sample}__TCR_clonotypes.csv')[['cdr3s_aa', 'frequency']])

    top_20_df1 = df_old_clonotypes.sort_values(by='frequency', ascending=False).head(20)
    return (pd.merge(top_20_df1, df_new_clonotypes, 
                     how ='left', on = 'cdr3s_aa')[['cdr3s_aa','frequency_x','frequency_y']].fillna(0))


 