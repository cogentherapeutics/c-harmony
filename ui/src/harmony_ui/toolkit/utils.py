import os 
import tempfile
import os
import re
import base64
import streamlit as st
import botocore, boto3
from pathlib import Path


from toolkit.constants import ENVIRONMENT

def make_div_small(content):
    return st.markdown(f'''
        <div style="font-size:12px;color:#bfbfbf">
        {content}
        </div>''', unsafe_allow_html=True)


def hspace(n=1):
    return '&nbsp;'*n


def vspace(n=1):
    return st.markdown('<BR>'*n, unsafe_allow_html=True)


def convert_num(value):
    try:
        if not value or value == 'N/A': return 'N/A'
        if '%' in value: return value

        val_regex = re.compile("(?<=>)(?P<value>.*?)(?=<)")
        match = val_regex.search(value)
        num = match.group('value') if match else value
        num = int(float(num.replace(',', '')))

        if num >= .9*1e9:
            num = '%4.2f B' % (num / 1e9)
        elif num >= .9*1e6:
            num = '%4.2f M' % (num / 1e6)
        elif num >= .9*1e5:
            num = '%4.2fk' % (num / 1e3)
        else:
            num = "{:,}".format(num)

        if match:
            return val_regex.sub(num, value)
        return num
    except:
        return value


def get_download_href(filepath):
    """Get a link to download a file. Need to base64 encode the contents of the file"""
    fileh = open(filepath, 'rb')
    filebytes = fileh.read()
    b64 = base64.b64encode(filebytes).decode()
    href = f"data:file;base64,{b64}"
    return href


def display_download_file(filepath, linktext='Download'):
    filename = os.path.basename(filepath)
    href = get_download_href(filepath)
    md_text = f'<a href="{href}" download="{filename}">{linktext}</a>'
    st.markdown(md_text, unsafe_allow_html=True)


def display_service():
    version = {
        'production': {
            'name': 'harmony',
            'dns': 'excalibur'
        },
        'edge': {
            'name': 'harmony Edge',
            'dns': 'caliburn'
        }
    }['edge' if ENVIRONMENT == 'production' else 'production']
    return
    #return st.markdown(f"[{version['name']}](http://{version['dns']}/thesaurus)")

    import botocore, boto3

def s3_list(s3_file):
    try:
        bucket = s3_file.replace('s3://', '').split('/')[0]
        key = '/'.join(s3_file.replace('s3://', '').split('/')[1:])
        list = boto3.client('s3').list_objects(Bucket=bucket,Prefix=key)
        return list
    except botocore.exceptions.ClientError as e:
        raise

def list_s3_directories(s3_file):
    try:
        bucket = s3_file.replace('s3://', '').split('/')[0]
        key = '/'.join(s3_file.replace('s3://', '').split('/')[1:])
        list = boto3.client('s3').list_objects(Bucket=bucket,Prefix=key)
        print (list)
        directories = [obj['Key'] for obj in list.get('CommonPrefixes', [])]
        return directories
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