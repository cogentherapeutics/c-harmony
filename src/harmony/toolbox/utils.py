import pandas as pd
import boto3, botocore
import os 
from pathlib import Path
from .constants import  REFERENCE, RESULTS_DICT, COMPARISON


def fetch_bytes(filename):
    '''Extracts the raw text contents from an S3 key.'''
    if filename.startswith('s3://'):
        bucket = filename[len('s3://'):].split('/')[0]
        key = '/'.join(filename[len('s3://'):].split('/')[1:])
        return boto3.resource('s3').Object(bucket, key).get()['Body'].read()
    return None

def s3_file_exists(s3_file):
    try:
        bucket = s3_file.replace('s3://', '').split('/')[0]
        key = '/'.join(s3_file.replace('s3://', '').split('/')[1:])
        boto3.client('s3').head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise


def s3_download(s3_file, local_file):
    try:
        bucket = s3_file.replace('s3://', '').split('/')[0]
        key = '/'.join(s3_file.replace('s3://', '').split('/')[1:])
        Path(local_file).parent.mkdir(parents=True, exist_ok=True)
        boto3.client('s3').download_file(Bucket=bucket, Key=key, Filename=local_file)
    except botocore.exceptions.ClientError as e:
        raise
        
def s3_list(s3_file):
    try:
        bucket = s3_file.replace('s3://', '').split('/')[0]
        print (bucket)
        key = '/'.join(s3_file.replace('s3://', '').split('/')[1:])
        
        print (key)
        list = boto3.client('s3').list_objects(Bucket=bucket,Prefix=key)
        return list
    except botocore.exceptions.ClientError as e:
        raise
def get_datatypes(experiment, r1, ):


    metadata_file = f's3://captan/{r1}/{experiment}/metadata/{experiment}_fastqs.csv'
    if not s3_file_exists(metadata_file):
        r1 = 'CAPTAN-experiments-v0.30.0'
    metadata_file = f's3://captan/{r1}/{experiment}/metadata/{experiment}_fastqs.csv'   
    
    s3_download(metadata_file,f'metadata/{experiment}_fastqs.csv')

    fastqs = pd.read_csv(f"metadata/{experiment}_fastqs.csv")
    dtypes = fastqs['sample_id'].str.split('__').tolist()
    dtypes_df = pd.DataFrame(dtypes, columns=['sample', 'datatype'])
    return dtypes_df

def get_metadata(experiment,r1, r2 ):
    metadata_file = f's3://captan/{r1}/{experiment}/metadata/{experiment}_samples.csv'
    if not s3_file_exists(metadata_file):
        r1 = 'CAPTAN-experiments-v0.30.0'
    metadata_file = f's3://captan/{r1}/{experiment}/metadata/{experiment}_samples.csv'

    s3_download(metadata_file,f'metadata/{experiment}_samples.csv')

    meta = pd.read_csv(f"metadata/{experiment}_samples.csv")

    samples =set( meta['sample_id'])
    return list(samples), r1


def file_sanity_check(r1, r2, sample, task):
    experiment =sample.split('_')[0]
    if task == 'hash-demux':
        reference_name = f's3://captan/{r1}/{experiment}/preprocessing/{task}/{sample}/{sample}_{RESULTS_DICT[task]}'
        if not s3_file_exists(reference_name):
            r1 ='CAPTAN-experiments-v0.30.0'
            reference_name = f's3://captan/{r1}/{experiment}/preprocessing/{task}/{sample}/{sample}_{RESULTS_DICT[task]}'
        comparison_name = f's3://captan/{r2}/{experiment}/preprocessing/{task}/{sample}/{sample}_{RESULTS_DICT[task]}'
        # print (reference_name)
        # print (comparison_name)
        
    elif task == 'gex-analysis':
        reference_name = f's3://captan/{r1}/{experiment}/preprocessing/gex-tenx/{sample}/{sample}__GEX_cellranger_count/{sample}__{RESULTS_DICT[task]}'
        
        if not s3_file_exists(reference_name):
            r1 = 'CAPTAN-experiments-v0.30.0'
            reference_name = f's3://captan/{r1}/{experiment}/preprocessing/gex-tenx/{sample}/{sample}_{RESULTS_DICT[task]}'
        comparison_name = f's3://captan/{r2}/{experiment}/preprocessing/gex-tenx/{sample}/{sample}__GEX_cellranger_count/{sample}__{RESULTS_DICT[task]}'
        
    else:
        reference_name = f's3://captan/{r1}/{experiment}/preprocessing/{task}/{sample}/{sample}__{RESULTS_DICT[task]}'
        if not s3_file_exists(reference_name):
            r1 = 'CAPTAN-experiments-v0.30.0'
            reference_name = f's3://captan/{r1}/{experiment}/preprocessing/{task}/{sample}/{sample}_{RESULTS_DICT[task]}'
        comparison_name = f's3://captan/{r2}/{experiment}/preprocessing/{task}/{sample}/{sample}__{RESULTS_DICT[task]}'
    if s3_file_exists(reference_name) and s3_file_exists(comparison_name):
        return ( True, r1 , r2)
    else :
        return ( False, r1, r2)
    
    def get_experiment(sample):
        return (sample.split('_')[0])