import streamlit as st
import pandas as pd
from matplotlib_venn import venn2 

from  toolkit.constants import RESULT_DIR, ENVIRONMENT
from toolkit.utils import s3_list, list_s3_directories, s3_download
from toolkit.query import (
    
    get_samplenames,
      read_queue, 
      get_clonotype_frequency,  
      get_json,
      json_to_df,
      get_clonotypes_union
            )

from matplotlib import pyplot as plt

experiments = read_queue()


def display_experiment_content(experiment):
    s3_download(f'{RESULT_DIR}/{ENVIRONMENT}/{experiment}/{experiment}_datatypes.csv',f'tmp/{experiment}_datatypes.csv' )
    df = pd.read_csv(f'tmp/{experiment}_datatypes.csv')
    grouped_df = df.groupby('sample')['datatype'].agg(list).reset_index()
    st.dataframe(grouped_df)
    summary = get_json(experiment, f'{experiment}_sample_status.json')
    st.write(json_to_df(summary))
    return
    

# Define a function that performs some computation based on the selected option
def process_option(selected_option):
    # Replace this with your actual computation based on the selected option
    result = f"{selected_option}"
    return result


# Main Streamlit app
st.title("Cipher  Harmony ")
# Create a selectbox in the sidebar to choose an option
selected_experiment = st.sidebar.selectbox("Select an option:", experiments)

# Button to trigger the computation based on the selected option
experiment = process_option(selected_experiment)

# Display the result in the main area
st.header(experiment)
st.write ("Sample information: ")

samples = get_samplenames(experiment)

#st.table(samples)

tabs = {f"tab{i+1}": sample_name for i, sample_name in enumerate(samples)}
selected_samples = st.sidebar.selectbox("Select a Sample",list(tabs.values()))
sample = process_option(selected_samples)
st.subheader    (f"{sample}")
############################################################
# Display summary of re-processing 
############################################################

display_experiment_content(experiment)


############################################################
# Displaying conolotype r value table per sample
############################################################
st.markdown    ("###### TCR clonotype frequency:")
clono_rvalue = get_json(experiment, f'{experiment}_tcr_clonotype_rvalue.json')
df = (json_to_df(clono_rvalue))
st.write(df[df['Sample'] == sample])

############################################################
# Displaying tcrid r value table per sample
############################################################
st.markdown    ("###### TCR - UMI  r value:")
tcrid_rvalue = get_json(experiment, f'{experiment}_tcr_barcode_umi_rvalue.json')
df = (json_to_df(tcrid_rvalue))
st.write(df[df['Sample'] == sample])


############################################################
# Displaying tcrid jaccard similarity
############################################################
st.markdown("###### TCR jaccard similarity:")
tcrid_js = get_json(experiment, f'{experiment}_tcrid_jaccard_similarity.json')
df = (json_to_df(tcrid_js))
st.write(df[df['Sample'] == sample])


#############################################################
#Displaying the top20 clonotype frequency plots from CR3 (old run) to CR7(new run)
#############################################################
col1, col2 = st.columns([1, 1])
with col1:
    top20 = get_clonotype_frequency(sample)
    fig, ax = plt.subplots(figsize=(8, 6))
    top20 = top20.rename(columns={'frequency_x':'frequency_cr3', 'frequency_y':'frequency_cr7'})
    top20.plot(kind='barh', ax=ax, x="cdr3s_aa", y=["frequency_cr3", "frequency_cr7"])

    ax.set_xlabel('clonotype')
    ax.set_ylabel('Frequency')
    ax.set_title('Bar Plot')
    plt.tight_layout()
    
    st.markdown("###### Top20 clonotypes frequncy")

    # Display plot in Streamlit
    st.pyplot(fig)

#############################################################
#Display the venndiagram of clonotypes
#############################################################
with col2:
    fig, ax = plt.subplots(figsize=(4, 6))
    clonotypes = get_clonotypes_union(sample)
    clonoset1 =  set((clonotypes[clonotypes['x']>0])['cdr3s_aa'])
    #clonoset_cr3 = set(clonotypes[~clonotypes['cdr3s_aa'].isin(clonoset1)])

    #filtered_df = df[~df['col2'].isin(values_to_exclude)]
    print (len(clonoset1))

    clonoset2 =  set((clonotypes[clonotypes['y']>0])['cdr3s_aa'])
    #clonoset_cr7 = set(clonotypes[~clonotypes['cdr3s_aa'].isin(clonoset2)])
    print (len(clonoset2))
    st.markdown("###### Venn diagram for  TCR clonotypes")
    # Create a Venn diagram
    venn2(subsets=(len(clonoset1 - clonoset2), len(clonoset2 - clonoset1), len(clonoset1 & clonoset2)),
        set_labels=('CR3', 'CR7'), ax=ax)
    st.pyplot(fig
        # Display the Venn diagram to the side of the page


)





############################################################
# Displaying gex-umi rvalues 
############################################################
st.write    (f"gex umi r-value:")
gex = get_json(experiment, f'{experiment}_gex_umi_rvalue.json')
print (gex)
df = (json_to_df(gex))
st.write(df[df['Sample'] == sample])
