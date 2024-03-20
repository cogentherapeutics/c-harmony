import os 
import tempfile
import os
import re
import base64
import streamlit as st


import os

RESULT_DIR = 's3://repertoire-application-storage/harmony'
ENVIRONMENT ='development'
# Initialize environment and folders
#ENVIRONMENT = os.environ.get('THESAURUS', 'edge')

REFERENCE  ='' 
# Constants
LIB_TYPES = ['TET', 'TCR', 'ADT', 'GEX']

