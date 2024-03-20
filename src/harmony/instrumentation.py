

import logging
import os

from toolbox.pipeline import orchestrate_pipeline

def instrumentation() -> None:
    print("c-harmony pipeline instrumented!")

    experiment = 'EXP21001952'
    reference = 'experiments-v0.40'
    comparison = 'CR7_refdata7'


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

if '__main__' == __name__:
    instrumentation()
