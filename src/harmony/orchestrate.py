#! /usr/bin/env python
# encoding: utf-8
"""
This tool generates the Sommelier tables used by the various UIs.

    pipenv run python /root/src/harmony_pipeline/orchestrate.py experiment.txt

"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
import sys

from toolbox.pipeline import harmony

print ("CAPTAN HARMONY")

def main() -> None:

    """Parses for launcher parameters."""


    parser = ArgumentParser(
        description=__doc__, formatter_class=RawDescriptionHelpFormatter
    )

    parser.add_argument('-f', '--filename', help="Specify the name of the text file with list of experiments")

    options = parser.parse_args()

    if options.filename:
        filename = options.filename
        print (filename)
        try:
            with open(filename, 'r') as file:
                experiments = [line.strip() for line in file.readlines()]
            print(f"Contents of the file '{filename}':\n{experiments}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
    else:
        print("Error: Please provide the --filename argument to specify the text file.")
    #for experiment in experiments:
    harmony(experiments)
    return 



if "__main__" == __name__:
    main()