import io
import streamlit as st

import numpy as np
import pandas as pd
import ast , json
from pathlib import Path

from matplotlib import pyplot as plt

import botocore, boto3
from toolkit.constants import RESULT_DIR, ENVIRONMENT
from toolkit.utils import s3_download



def read_queue():
    s3_download(f"{RESULT_DIR}/development/queue.csv", 'queue.csv')

    try:
        with open('queue.csv', 'r') as file:
            experiments = [line.strip() for line in file.readlines()]
            return experiments
    except FileNotFoundError:
        print ("Queue.csv not found")
        return 


def get_samplenames(experiment):

    s3_download(f'{RESULT_DIR}/{ENVIRONMENT}/{experiment}/{experiment}_sample_status.json',f'{experiment}_sample_status.json')
    print (f'{RESULT_DIR}/{ENVIRONMENT}/{experiment}/{experiment}_sample_status.json')
    try:
        with open(f'{experiment}_sample_status.json', 'r') as json_file:
            json_data = json.load(json_file)
            sample_names = [item[0] for item in json_data]

            print (sample_names)
            return sample_names
    except  json.JSONDecodeError as e:
        print (f"Error decoding JSON: {e}")
        return 
def get_json(experiment, filename):
    print (f'{RESULT_DIR}/{ENVIRONMENT}/{experiment}/{filename}')
    s3_download(f'{RESULT_DIR}/{ENVIRONMENT}/{experiment}/{filename}',f'tmp/{filename}')
    try:
        with open(f'tmp/{filename}', 'r') as json_file:
            json_data = json.load(json_file)
            return json_data
    
    except  json.JSONDecodeError as e:
        print (f"Error decoding JSON: {e}")
        return

def get_clonotype_frequency(sample):
    experiment = sample.split('_')[0]
    s3_download(f'{RESULT_DIR}/{ENVIRONMENT}/{experiment}/{sample}_top20_clonotype_frequency.csv', f'tmp/{sample}_top20_clonotype_frequency.csv')
    

    top_20 = pd.read_csv(f'tmp/{sample}_top20_clonotype_frequency.csv')
    # fig, ax = plt.subplots()
    # st.write(top_20.head())
    # ax = top_20.plot(x="cdr3s_aa", y=["frequency_CR3", "frequency_CR7"], kind="barh", rot=0,)
    # ax.set_title(f'{sample}')
    # plt.tight_layout()
    return top_20

# def get_clonotype_rvalue(sample):
#     #EXP21002563_tcr_clonotype_rvalue.json
#     experiment = sample.split('_')[0]
#     s3_download(f'{RESULT_DIR}/{ENVIRONMENT}/{experiment}/{experiment}_tcr_clonotype_rvalue.json', f'tmp/{experiment}_tcr_clonotype_rvalue.json')
#     #clono_rvalue = get_sample_summary(experiment)
#     try:
#         with open(f'tmp/{experiment}_tcr_clonotype_rvalue.json', 'r') as json_file:
#             json_data = json.load(json_file)
#         return json_data
#     except  json.JSONDecodeError as e:
#         print (f"Error decoding JSON: {e}")
#         return


def json_to_df(json_data):
    data = []

    # Iterate over the nested list
    for sample, values in json_data:
        row_data = {'Sample': sample}  # Create a dictionary for each row with sample name
        row_data.update(values)  # Update the dictionary with values from the nested dictionary
        data.append(row_data)  # Append the dictionary to the data list

    # Create DataFrame
    df = pd.DataFrame(data)
    return df

def get_clonotypes_union(sample):
    experiment = sample.split('_')[0]
    s3_download(f'{RESULT_DIR}/{ENVIRONMENT}/{experiment}/{sample}_clonotypes_union.csv',f'tmp/{sample}_clonotypes_union.csv')
    
    df = pd.read_csv(f'tmp/{sample}_clonotypes_union.csv')
    return df

def get_experiments_backdoor():
    s3_download(f's3://repertoire-application-storage/backdoor/references/production/experiments-metadata.csv',f'tmp/experiments-metadata.csv')
    df = pd.read_csv(f'tmp/experiments-metadata.csv')
    return df