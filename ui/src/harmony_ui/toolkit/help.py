import pandas as pd
import streamlit as st


def help_help():
    state = {
        'Status': ['INREVIEW', 'ACCEPT', 'REJECT', 'STALE', 'INCOMPLETE', 'DNU'],
        'Manual QC': ['experiment is currently under review',
                      'after review, results accepted "as is"',
                      'after review, results rejected--REDO needed',
                      'previous review out of date, new review needed',
                      'some of the review has been performed, but is not complete',
                      'Do-Not-Use, results will not be loaded into the database']
    }

    st.markdown(f"""
        The aim of SeqR -- short for Seq(uencing)R(eview) -- is to help coordinate the assessment of 
        CIPHER runs by the Sequencing and Computational teams, prior to their wider use across 
        Repertoire. To do this, SeqR provides a consolidated summary of QC metrics and analysis 
        outcomes for each run, which each team inspects to judge whether the run is sufficiently 
        high in quality to warrant further use (PASS) or not (FAIL). Runs that are deemed to FAIL 
        will be marked as such on Backdoor and associated dashboards, and usually not loaded into 
        the database or other analysis tools; depending upon the nature of the problem, a FAILed run 
        may be re-sequenced and/or re-analyzed. For more details on this process, see the 
        <a target='_blank' href='http://compsci/captan/img/state-machine.png'>CAPTAN state diagram</a>.
        A short introduction to using SeqR can also be viewed in this 
        <a target='_blank' href='http://compsci/captan/img/seqr.pdf'>tutorial</a>. 
        
        **QC Thresholds** 
        
        The following metrics are considered a <font color='red'>**FAIL**</font> or 
        <font color='orange'>**WARN**</font>ing if they meet the below values. 

        Reads Mapped to Any V(D)J Gene: <font color='orange'>< 50% (TCR)</font> , 
        <font color='red'>< 20% (TCR -- not a pipeline failure)</font> 

        Est. # Cells: <font color='orange'>> 60k (TCR/GEX)</font> ,  <font color='red'>< 100 (GEX)</font> 

        Barcode Read Count: <font color='red'>< 20k (ADT/TET)</font> 
        
        **Metric Definitions**
        

        Table columns are defined <a target='_blank' href='https://www.notion.so/cogen/SeqR-72ab114804d840d98f7e97b2ea471b3a'>
        here</a>. These definitions can also be found by hovering over the column header. 
        
        **QC Review Status**
        """, unsafe_allow_html=True)

    state = pd.DataFrame(state).set_index('Status')
    st.table(state)


def harmony_help():
    state = {
        'Status': ['CDNA_PASS/FAIL/UNKNOWN', 'NotRequested', 'Prepped_PASS/FAIL', 'Pooled', 'Complete'],
        'Sequencing Status': [
            'Passed cDNA Cleanup',
            'Library type was not requested',
            'Passed cDNA Cleanup and library preparation',
            'Sample library type was put into a pool but the BCL entry is incomplete',
            'Library completed sequencing and ELN is completely filled'
        ]
    }

    st.markdown(f"""
        C'mon -- the CIPHER monitoring app -- gives a detailed view of library sequencing status, 
        KPIs across experiments, and year-to-date KPI summary by project, as well as the log file
        of the Benchling data extraction that determines the lane status. 
        
        **Lane Status View** 

        Each lane includes one of the following library statuses: 
    """)

    state = pd.DataFrame(state).set_index('Status')
    st.table(state)

    st.markdown(f"""
        Along with the sequencing lane status, the ALP status is also shown. For each lane, 
        if an ALP/ALS on Benchling has been modified since its last extraction to s3 or it does not exist 
        within our system, a message is shown. 

        *If the lane status is not as expected, please check that the ELN is correctly filled out and alert 
        someone on the CompSci team...*

        **KPI View**

        Finally, the KPI view gives a summary of the number of lanes and runs, project type, and additional 
        metadata of each experiment or each project YTD.
    """)


def summary_help():
    st.markdown(f"""
        SquID -- short for Sequencing Inventory Data -- aims to help the sequencing team identify which 
        sequencing lanes have completed sequencing and are ready for analysis.
    """, unsafe_allow_html=True)