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
        centroids_data_input_name = "{MODEL TABLE}"
    else:
        main_input_name = recipe_config["input_table_names"][0]["table"]
        input_database_name = recipe_config["input_table_names"][0]['schema']
        main_output_name = recipe_config["output_table_names"][0]["table"]
        output_database_name = recipe_config["output_table_names"][0]['schema']
        val_location = recipe_config["val_location"]
        if (len(recipe_config["input_table_names"]) >= 2) and ("table" in recipe_config["input_table_names"][1]):
            centroids_data_input_name = recipe_config["input_table_names"][1]["table"]
        else:
            centroids_data_input_name = ""
        

    # KMeans
    database = input_database_name
    tablename = main_input_name
    outputdatabase = output_database_name
    outputtablename = main_output_name


    columns = ",".join(recipe_config['kmeans_columns'])
    centers = recipe_config.get('kmeans_centers','3')

    optional_args = ""

    if centroids_data_input_name:
        optional_args += "continuation=" + centroids_data_input_name + ";"
        
    if 'kmeans_max_iter' in recipe_config and recipe_config['kmeans_max_iter'] != 50:
        optional_args += "iterations=" + str(recipe_config['kmeans_max_iter']) + ";"

    if 'kmeans_threshold' in recipe_config and recipe_config['kmeans_threshold'] != 0.001:
        optional_args += "threshold=" + str(recipe_config['kmeans_threshold']) + ";"

    optional_args += "operatordatabase=" + val_location + ";"


    query = """call {}.td_analyze('KMEANS', 
    'database={};
    tablename={};
    outputdatabase={};
    outputtablename={};
    columns={};
    kvalue={};
    {}')""".format(verifyAttribute(val_location), verifyAttribute(database), verifyAttribute(tablename), verifyAttribute(outputdatabase), verifyAttribute(outputtablename), verifyAttribute(columns), verifyAttribute(centers), verifyAttribute(optional_args))

    
    if not valib_query_wrapper:
        return query
    
    valib_query_wrapper.execute(query)



