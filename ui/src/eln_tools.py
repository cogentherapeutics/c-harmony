#!/usr/bin/env python

import requests
import pandas as pd

from functools import reduce
from itertools import product, chain, starmap


APIRoot="https://repertoire.benchling.com/api/v2"
Key='sk_rGISt5YEsMQ5XWghM0208xLjh3tA0'


def get_eln_id(eln):
    '''Extracts the Benchling Warehouse ID for an ELN from its JSOn form.
    Args:
        eln (dict): A nested dictionary derived from the ELN JSON.
    Return: (str) A string representing the ELN ID.
    '''
    return eln['entries'][0]['id']


def get_eln_version(eln):
    try:
        raw_text = eln['entries'][0]['days'][0]['notes'][0]['text']
        free_text_category = raw_text.split(':')[0].strip()
        version = raw_text.split(':')[1].strip().split(' ')[0].strip()
        category = {
            'Research Template Version': 'research',
            'Template Version': 'clinical'
        }[free_text_category]
        return f"{category}__{version}"
    except:
        eln_version = get_eln_new_version(eln)
        return eln_version


def get_eln_new_version(eln):
    '''Extracts a "ELN Information" table from an ELN as a dataframe or returns None
    Args:
        eln (dict): A nested dictionary derived from the ELN JSON.
    Return: (list[str]) A list of strings representing the Sequencing pools
        which have been extracted from the ELN.
    '''
    try:
        eln_tab = get_table(eln, 'ELN Information')
        category =  eln_tab.iloc[0,0]
        version = eln_tab.iloc[0,1]
        return f"{category}__{version}"
    except:
        category =  get_table(eln, 'ELN Information').ELN_Template.values[0]
        version =  get_table(eln, 'ELN Information').Version.values[0]
        return f"{category}__{version}"


def get_table(eln, name):
    '''Extracts a specific table from an ELN as a dataframe or returns None
    when the table is not found.
    Args:
        eln (dict): A nested dictionary derived from the ELN JSON.
        name (str): A string representing the ELN case dependent table name.
    Return: (dataframe or None) A dataframe with the tables data, or None
        in the failure case.
    '''
    try:
        note = next(
            chain(*[
                [note for note in day['notes']
                if 'table' == note['type'] and name == note['table']['name']]
                for day in eln['entries'][0]['days']
            ])
        )
        return pd.DataFrame(columns=note['table']['columnLabels'],
                 data=[[cell['text'] for cell in row['cells']]
                        for row in note['table']['rows']])
    except StopIteration:
        return None


def fetch_eln(experiment):
    '''Retrieve the JSON for an ELN.
    Args:
        experiment (str): An ELN identifier in the form EXP########.
    Return: (dict) A nested dictionary formed from the ELN JSON.
    '''
    session = requests.Session()
    session.auth = (Key, None)
    eln = session.get(f"{APIRoot}/entries:bulk-get?displayIds={experiment}").json()
    if 'error' in eln:
        raise InvalidELNError(f"ELN does not exist: {experiment}")
    return eln


def fetch_sample_staining_metadata(cursor, sample_names, version):    
    antigens = ['antigen_library_set$raw', 'antigen_library_pool$raw', 'dextramer$raw']
    antibodies = ['adt$raw', 'adt_pool$raw','adt_batch$raw']

    antigen_batches = ['dextramer$batch$raw']
    antibody_batches = ['adt$batch$raw', 'adt_pool$batch$raw']

    batch_ref = {
        'dextramer$batch$raw': 'dextramer$raw',
        'adt$batch$raw': 'adt$raw',
        'adt_pool$batch$raw': 'adt_pool$raw'
    }  

    parameters = list(chain(*starmap(
        lambda antigens, is_antigen_batch, antibodies, is_antibody_batch:
            chain(starmap(
                lambda ag, ab:
                    {
                        'antigen': ag,
                        'is_antigen_batch': is_antigen_batch,
                        'antibody': ab,
                        'is_antibody_batch': is_antibody_batch
                    },
                product(antigens, antibodies)
            )),
        [
            (antigen_batches, True, antibody_batches, True),
            (antigen_batches, True, antibodies, False),
            (antigens, False, antibody_batches, True),
            (antigens, False, antibodies, False),
            (antigen_batches, True, [None], False),
            ([None], False, antibody_batches, True),
            (antigens, False, [None], False),
            ([None], False, antibodies, False)
        ]   
    )))


    def _generate_selection(parameters):
        antigen = parameters['antigen']
        is_antigen_batch = parameters['is_antigen_batch']
        antibody = parameters['antibody']
        is_antibody_batch = parameters['is_antibody_batch']

        return ', '.join(chain(
            [
                "_10x_sample_cells_adt_tet$raw.name$ as sample_name",
                "_10x_sample_cells_adt_tet$raw.file_registry_id$ as sample_registry_id"
            ],
            [ " clinical_sample.name$ as clinical_name," ]
                if 'clinical__2.0' == version
                else [],
            [ f"{batch_ref[antigen] if is_antigen_batch else antigen}.file_registry_id$ as antigen_pool" ]
                if antigen
                else [],
            [ f"{batch_ref[antibody] if is_antibody_batch else antibody}.file_registry_id$ as adt_pool" ]
                if antibody
                else []
        ))


    def _generate_tables(parameters):
        antigen = parameters['antigen']
        is_antigen_batch = parameters['is_antigen_batch']
        antibody = parameters['antibody']
        is_antibody_batch = parameters['is_antibody_batch']

        return ', '.join(chain([
                '_10x_sample_cells_adt_tet$raw',   
            ],
            ['_10x_clinical_sample_mix$raw', ' clinical_sample']
                if 'clinical__2.0' == version
                else [],
            [ antigen ] if antigen else [],
            [ batch_ref[antigen] ] if (antigen and is_antigen_batch) else [],
            [ antibody ] if antibody else [],
            [ batch_ref[antibody] ] if (antibody and is_antibody_batch) else []
        ))


    def _generate_filtering_criteria(parameters):
        antigen = parameters['antigen']
        is_antigen_batch = parameters['is_antigen_batch']
        antibody = parameters['antibody']
        is_antibody_batch = parameters['is_antibody_batch']


        return ' AND '.join(chain(
            [f"_10x_clinical_sample_mix$raw.entity = _10x_sample_cells_adt_tet$raw.id" ]
                if 'clinical__2.0' == version
                else [],
            [ f"_10x_clinical_sample_mix$raw.clinical_sample_1 = clinical_sample.id" ]
                if 'clinical__2.0' == version
                else [],
            [ f"_10x_sample_cells_adt_tet$raw.input_antigen_set = {antigen}.id" ]
                if antigen
                else [],
            [ f"{antigen}.entity_id$ = {batch_ref[antigen]}.id" ]
                if (antigen and is_antigen_batch)
                else [],
            [ f"_10x_sample_cells_adt_tet$raw.input_adt = {antibody}.id" ]
                if antibody
                else [],
            [ f"{antibody}.entity_id$ = {batch_ref[antibody]}.id" ]
                if (antibody and is_antibody_batch)
                else []
        ))


    def _query_remaining_samples(samples_and_results, parameter):
        remaining_samples = samples_and_results[0]
        results = samples_and_results[1]

        if remaining_samples:
            selection = _generate_selection(parameter)
            tables = _generate_tables(parameter)
            cells = f"""_10x_sample_cells_adt_tet$raw.name$ IN ('{"', '".join(remaining_samples)}')"""
            filtering_criteria = _generate_filtering_criteria(parameter)
            query = f"SELECT {selection} FROM {tables} WHERE {cells} AND {filtering_criteria}"

            columns = ['sample_name', 'sample_registry_id', 'antigen_pool', 'adt_pool', 'clinical_name']
            cursor.execute(query)
            df = pd.DataFrame(columns=columns, data=cursor.fetchall())

            return (
                set(remaining_samples).difference(set(df.sample_name)), # remaining samples
                results + [df]
            )
        else:
            return (
                remaining_samples,
                results
            )


    remaining_samples, results = reduce(
        _query_remaining_samples,
        parameters,
        (sample_names, [])
    )

    return pd.concat(results)