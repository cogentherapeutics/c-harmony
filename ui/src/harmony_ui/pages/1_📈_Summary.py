import streamlit as st
import time, os
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from toolkit.constants import RESULT_DIR, ENVIRONMENT
from toolkit.query import get_json, read_queue, json_to_df, get_experiments_backdoor
from toolkit.utils import s3_download


try:
    # Create the directory
    os.makedirs(f'tmp')
    print(f"Directory tmp created successfully.")
except FileExistsError:
    print(f"Directory tmp already exists.")
st.set_page_config(page_title="Summary", page_icon="📈")

st.markdown("# Re-processing Summary")
st.sidebar.header("Help")
st.write(
    """This page generates a summary of total experiments re-processed and it's status compared to exsting cipher Runs.  Enjoy!"""
)
def display_experiment_content(experiment):
    s3_download(f'{RESULT_DIR}/{ENVIRONMENT}/{experiment}/{experiment}_datatypes.csv',f'tmp/{experiment}_datatypes.csv' )
    df = pd.read_csv(f'tmp/{experiment}_datatypes.csv')
    grouped_df = df.groupby('sample')['datatype'].agg(list).reset_index()

    st.dataframe(grouped_df)
    
def create_pie_chart(categories, counts):
    # Create a pie chart
    fig, ax = plt.subplots()
    ax.pie(counts, labels=categories, autopct='%1.1f%%', startangle=200)
    ax.set_title('Pie Chart: summary of re-processing')
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    return fig


pre_experiments = read_queue()
tot_experiments = get_experiments_backdoor()

st.markdown(f"**Total number of experiments {len(tot_experiments)}**.")
st.markdown(f"**Total number of experiment re-processed {len(pre_experiments)}**.")



########################################################################
#Display pie chart for re-processed experiments
###################################################################



categories = ['Remaining', 'Re-processed']
counts = [len(tot_experiments), len(pre_experiments)]

fig = create_pie_chart(categories, counts)

st.pyplot(fig)