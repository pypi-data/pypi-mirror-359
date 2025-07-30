# -*- coding: utf-8 -*-
'''
Copyright © 2024 by Teradata.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from query_engine_wrapper import QueryEngineWrapper
from verifyTableColumns import *


def execute(recipe_config, valib_query_wrapper=None):
    if not valib_query_wrapper:
        input_database_name = "{INPUT DATABASE}"
        main_input_name = "{INPUT TABLE}"
        output_database_name = "{OUTPUT DATABASE}"
        main_output_name = "{OUTPUT TABLE}"
        val_location = "{VAL DATABASE}"
    else:
        main_input_name = recipe_config["input_table_names"][0]["table"]
        input_database_name = recipe_config["input_table_names"][0]['schema']
        main_output_name = recipe_config["output_table_names"][0]["table"]
        output_database_name = recipe_config["output_table_names"][0]['schema']
        val_location = recipe_config["val_location"]
        
    # Histogram

    database = input_database_name
    tablename = main_input_name
    outputdatabase = output_database_name
    outputtablename = main_output_name

    columns = ",".join(recipe_config['histogram_columns'])

    optional_args = ""

    if 'bins' in recipe_config and recipe_config['histogram_bins']:
        optional_args += "bins=" + str(recipe_config['histogram_bins']) + ";"

    if 'bins_with_boundaries' in recipe_config and recipe_config['histogram_bins_with_boundaries']:
        histogram_bins_with_boundaries = recipe_config['histogram_bins_with_boundaries']
        # No quotes single or double
        if ('"' in histogram_bins_with_boundaries) or ('"' in histogram_bins_with_boundaries):
            raise Exception('Illegal histogram bins with boundaries', histogram_bins_with_boundaries)
        optional_args += "binwithminmax=" + ",".join(histogram_bins_with_boundaries) + ";"

    if 'boundaries' in recipe_config and recipe_config['histogram_boundaries']:
        histogram_boundaries = recipe_config['histogram_boundaries']
        # No quotes single or double
        if ('"' in histogram_boundaries) or ('"' in histogram_boundaries):
            raise Exception('Illegal histogram boundaries', histogram_boundaries)
        optional_args += "boundaries=" + ",".join(histogram_boundaries) + ";"

    if 'quantiles' in recipe_config and recipe_config['histogram_quantiles']:
        optional_args += "quantiles=" + str(recipe_config['histogram_quantiles']) + ";"

    if 'widths' in recipe_config and recipe_config['histogram_widths']:
        optional_args += "widths=" + str(recipe_config['histogram_widths']) + ";"

    if 'overlay_columns' in recipe_config and recipe_config['histogram_overlay_columns']:
        optional_args += "overlaycolumns=" + ",".join(recipe_config['histogram_overlay_columns']) + ";"

    if 'stats_columns' in recipe_config and recipe_config['histogram_stats_columns']:
        optional_args += "statisticscolumns=" + ",".join(recipe_config['histogram_stats_columns']) + ";"

    if 'hist_style' in recipe_config and recipe_config['histogram_hist_style']:
        optional_args += "style=" + str(recipe_config['histogram_hist_style']) + ";"

    if 'filter' in recipe_config and recipe_config['histogram_filter']:
        histogram_filter = recipe_config.get('histogram_filter')
        # Santize user specified string: No double quotes or odd number of single quotes
        if ('"' in histogram_filter) or (histogram_filter.count("'") % 2 == 1) or (';' in histogram_filter):
            raise Exception('Illegal Filter', histogram_filter)
        optional_args += "where=" + str(histogram_filter) + ";"


    query = """call {}.td_analyze('HISTOGRAM', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    columns={};
    {}')""".format(verifyAttribute(val_location), verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(columns), verifyAttribute(optional_args))

    
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



