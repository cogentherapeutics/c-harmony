#! /usr/bin/env python3

import csv
import boto3
import base64
import botocore

from io import StringIO
from pathlib import Path

# Establish connection to our Amazon S3 resource
s3 = boto3.client('s3')

DEFAULT_ROOT = 'experiments-v0.40'
DEFAULT_BUCKET = 'captan'


def check_roots(root, experiment, folder=None):
    '''
    If we are running default folder and the experiment does not exist,
    then check previous CAPTAN versions. 
    '''
    # Check all old CAPTAN releases for re-runs, with the root having higher priority 
    all_roots = ['experiments-v0.40', 'CAPTAN-experiments-v0.30.0']
    if root in all_roots:
        all_roots = list(dict.fromkeys([root] + all_roots))
        for captan_root in all_roots:
            root_folders = ls(f's3://captan/{captan_root}/{experiment}/')
            if root_folders:
                if folder in root_folders or not folder:
                    return captan_root, root_folders
    return root, None


def ls(filename):
    '''List the contents for an S3 location.
        ls('s3://captan/CAPTAN-experiments-v0.30.0/EXP20001377/preprocessing/')
    Given how the AWS S3 API works the path must have a trailing forward
    slash if you would like to see the contents of an S3 key acting as
    a directory. Otherwise only the closest path that uses your filename
    argument as a prefix will be shown if it exists. For example this:
        ls('s3://captan/CAP')
    will complete and return:
        ['CAPTAN-experiments-v0.30.0']
    '''
    bucket = filename.replace('s3://', '').split('/')[0]
    key = '/'.join(filename.replace('s3://', '').split('/')[1:])
    result = boto3.client('s3').list_objects_v2(Bucket=bucket, Prefix=key, Delimiter='/')
    
    if 'CommonPrefixes' in result:
        return sorted([
            x['Prefix'].split('/')[-2]
            for x
            in result \
            ['CommonPrefixes']
        ])
    
    if 'Contents' in result:
        return sorted([
            x['Key'].split('/')[-1] for x in result['Contents']
        ])


def check_file_exists(filename):
    try:
        bucket = filename.replace('s3://', '').split('/')[0]
        key = '/'.join(filename.replace('s3://', '').split('/')[1:])
        boto3.client('s3').head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise


def fetch_text(filename):
    '''Extracts the raw text contents from an S3 key.'''
    if filename.startswith('s3://'):
        bucket = filename[len('s3://'):].split('/')[0]
        key = '/'.join(filename[len('s3://'):].split('/')[1:])
        return boto3.resource('s3').Object(bucket, key).get()['Body'].read().decode('utf8')
    else:
        with open(filename) as f:
            text = f.read()
        return text


def fetch_bytes(filename):
    '''Extracts the raw text contents from an S3 key.'''
    if filename.startswith('s3://'):
        bucket = filename[len('s3://'):].split('/')[0]
        key = '/'.join(filename[len('s3://'):].split('/')[1:])
        return boto3.resource('s3').Object(bucket, key).get()['Body'].read()
    return None


def fetch_csv(filename):
    """Extracts the text from an S3 key as a CSV where the rows are returned
    as a list of dictionaries that use the column headers as the field keys.
    """
    return list(csv.DictReader(StringIO(fetch_text(filename))))


def fetch_pdf(filename):
    '''Extracts the raw text contents from an S3 key.'''
    # Opening file from file path
    f = fetch_bytes(filename)
    if f:
        base64_pdf = base64.b64encode(f).decode('utf-8')
        # Embedding PDF in HTML
        return f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    return None


def fetch_timestamp(filename):
    '''Fetches the timestamp of a file'''
    try:
        bucket = filename.replace('s3://', '').split('/')[0]
        key = '/'.join(filename.replace('s3://', '').split('/')[1:])
        response = boto3.client('s3').head_object(Bucket=bucket, Key=key)
        return response["LastModified"]
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return None
        else:
            raise
    

def s3_upload(text, s3_file):
    try:
        bucket = s3_file.replace('s3://', '').split('/')[0]
        key = '/'.join(s3_file.replace('s3://', '').split('/')[1:])
        boto3.resource('s3').Bucket(bucket).put_object(Body=text, Key=key)
    except botocore.exceptions.ClientError as e:
        raise


def s3_download(s3_file, local_file):
    try:
        bucket = s3_file.replace('s3://', '').split('/')[0]
        key = '/'.join(s3_file.replace('s3://', '').split('/')[1:])
        Path(local_file).parent.mkdir(parents=True, exist_ok=True)
        boto3.client('s3').download_file(Bucket=bucket, Key=key, Filename=local_file)
    except botocore.exceptions.ClientError as e:
        raise


def s3_remove(s3_file):
    try:
        bucket = s3_file.replace('s3://', '').split('/')[0]
        key = '/'.join(s3_file.replace('s3://', '').split('/')[1:])
        boto3.resource('s3').Object(bucket, key).delete()
    except botocore.exceptions.ClientError as e:
        raise