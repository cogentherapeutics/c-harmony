# c-harmony

A tool for comparing two different cipher runs for an experiment.

This tool has two parts,
1. "harmony" pipeline to run comparison between two cipher runs of experiment lists provided

   pipenv run python src/harmony/orchestrate.py -f <experilent_list.txt>
    Pipeline runs comparison of different datatypes, TCR , Clonotypes, Hits and GEX. Generated results and csv files will be pr-estored under "s3://repertoire-application-storage/harmony/development/<EXPID/.

2. UI to Select the experi,ent and visualize the comparison results.

## TODO:

Currently the tool runs for existing cipher results Vs Upcming re-processing. Will be extended to add any cipher runs (providing the root directory for new run and old run). 
A TCRID/Clonotype will be provided to search the same in new runs. 
