#! /usr/bin/env python
# encoding: utf-8
"""
This tool generates the Sommelier tables used by the various UIs.

    pipenv run python /root/src/harmony_pipeline/orchestrate.py experiment.txt

"""
from toolbox.constants import  RESULT_DIR, REFERENCE, COMPARISON
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
import sys, subprocess, os
import logging

from toolbox.pipeline import orchestrate_pipeline



def main() -> None:

    

    """Main c-harmony task orchestration  ."""

    print ("CAPTAN HARMONY")


    parser = ArgumentParser(
        description=__doc__, formatter_class=RawDescriptionHelpFormatter
    )

    parser.add_argument('-e', '--experiment',type =str, help = 'experiment name to run comparsion')
    parser.add_argument('-r', '--reference',type =str, help = 'reference root direcotry to run the comparsion against')
    parser.add_argument('-c', '--comparison',type =str, help ='root directory to run comparison')
    #parser.add_argument('-e', '--experiment',type =str)




    options    = parser.parse_args()
    experiment = options.experiment
    reference  = options.reference
    comparison = options.comparison


    formatter = logging.Formatter(
    fmt="%(levelname)s - %(asctime)s - %(module)s %(name)s : %(message)s",
    datefmt="%Y-%b-%d %H:%M:%S",
    )


    os.makedirs(f"tmp", exist_ok=True)
    os.makedirs(f"{experiment}/results", exist_ok=True)
    
    try:
        # Create the directory
        os.makedirs(f'results')
        print(f"Directory harmony_results created successfully.")
    except FileExistsError:
        print(f"Directory results already exists.")

    ######################################################################################
    #####Create metadata file for storing information of an experiment ##################
    ######################################################################################

    try: 
        os.makedirs(f'tmp/{experiment}/metadata')
        
    except:
         print(f"Directory 'tmp/metadata already exists.")


    harmony_log_path = f"results/{experiment}/harmony.log"
    cfh = logging.FileHandler(harmony_log_path, mode="w")
    cfh.setLevel(logging.INFO)
    cfh.setFormatter(logging.Formatter(fmt="%(message)s"))


    error_log_path = f"results/{experiment}/error.log"
    efh = logging.FileHandler(error_log_path, mode="w")
    efh.setLevel(logging.INFO)
    efh.setFormatter(formatter)

    logging.basicConfig(
        encoding="utf-8",
        format=formatter._fmt,
        datefmt=formatter.datefmt,
        level=logging.INFO,
    )

    harmony_logger = logging.getLogger("harmony")
    harmony_logger.addHandler(cfh)

    error_logger = logging.getLogger("errors")
    error_logger.addHandler(efh)


    orchestrate_pipeline(
        harmony_log_path,
        error_log_path,
        reference,
        comparison,
        experiment
    )


if "__main__" == __name__:
    main()