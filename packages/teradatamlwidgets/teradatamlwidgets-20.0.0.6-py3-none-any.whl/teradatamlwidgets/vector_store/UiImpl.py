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

Primary Owner: Saroop Samra (saroop.samra@teradata.com)
Secondary Owner: 
'''

import os
import sys
import json
from pathlib import Path
import ipywidgets as widgets
import IPython
from IPython.display import clear_output, HTML, Javascript, display
import pandas as pd
from teradatagenai.vector_store.vector_store import VSManager, VectorStore
from teradataml import *
from teradatamlwidgets.custom_destroy_button import *
from teradatamlwidgets.base_ui import _BaseUi
import traceback



class _UiImpl(_BaseUi):
    """
    Private class that implements teradatamlwidgets Vector Store UI.
    """
    def __init__(self):
        """
        DESCRIPTION:
            Constructor for private class that implements teradatamlwidgets Vector Store UI.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._ccp_enabled = False
        self._host = "localhost"
        self._base_url = ""
        self._recent_similarity_search_result = None
        self.vs_df = None
        self.vs_list = []
        self.vector_store_objects = {}
        self.right_pane_tabs = widgets.Tab()
        self.output_widget = widgets.Output()
        self._answers = {}

        _BaseUi.__init__(self, default_database="", connection=None)

        if self._connection.is_logged_in():
            self._create_ui()
            self._open_ui()

    def _init_ui(self):
        """
        DESCRIPTION:
            Private function that calls either ccp enabled or non ccp enabled accordingly in UI for Vector Store.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._populate_main_ui()

    def _populate_ccp_ui(self):
        """
        DESCRIPTION:
            Private function that is called when it is ccp in UI for Vector Store, which brings up necessary parameters to login.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        base_url_input = widgets.Text(description="Base URL:", value=self._base_url)
        pat_token_input = widgets.Text(description="PAT Token:", value="")
        pem_file_input = widgets.Text(description="PEM File:")
        pem_file_button = widgets.FileUpload(description="Upload PEM")
        start_button = widgets.Button(description="Start")

        def on_pem_upload(change):
            pem_file_input.value = list(pem_file_button.value.keys())[0]

        def on_start_click(_):
            try:
                print("Connecting to Vector Store...")
                self.populate_main_ui()
            except Exception as e:
                with self.output_widget:
                    clear_output()
                    print(f"ERROR: {e}")

        pem_file_button.observe(on_pem_upload, names="value")
        start_button.on_click(on_start_click)
        display(widgets.VBox([base_url_input, pat_token_input, widgets.HBox([pem_file_input, pem_file_button]), start_button, self.output_widget]))
        self._populate_main_ui()

    def _populate_non_ccp_ui(self):
        """
        DESCRIPTION:
            Private function that is called when it is non ccp in UI for Vector Store, which brings up login.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        username_input = widgets.Text(description="Username:", value="oaf")
        host_input = widgets.Text(description="Host:", value=self._host)
        password_input = widgets.Password(description="Password:", value="oaf")
        database_input = widgets.Text(description="Database:", value="oaf")
        base_url_input = widgets.Text(description="Base URL:", value=self._base_url)
        start_button = widgets.Button(description="Start")

        def _on_start_click(_):
            try:
                self.username = username_input.value
                self.host = host_input.value
                self.password = password_input.value
                self.database = database_input.value
                set_config_params(_vector_store_base_url=base_url_input.value)
                VSManager._connect(username=self.username, password=self.password, database=self.database, host=self.host)
                self._populate_main_ui()
            except Exception as e:
                with self.output_widget:
                    clear_output()
                    self.last_error = traceback.format_exc()
                    print(f"ERROR: {e}")

        start_button.on_click(on_start_click)

        self._main_ui = widgets.VBox([username_input, host_input, password_input, database_input, base_url_input, start_button, self.output_widget])

    def _populate_main_ui(self):
        """
        DESCRIPTION:
            Private function that populates the whole UI for Vector Store, including the header logos, left pane and right pane.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        border_style = widgets.Layout(border=_UiImpl._ui_border, padding="10px")
        #header = widgets.HTML("<h3>Teradata Enterprise Vector Store</h3>")
        #header.style = {'color': 'orange'}
        header = widgets.HTML("<h2 style='color: OrangeRed;'>Teradata Enterprise Vector Store</h2>", layout=widgets.Layout(flex='1 1 0%', width='auto'))

        with open(os.path.join(self._folder, 'logo.png'), 'rb') as f:
            logo = f.read()
  
        teradata_logo = widgets.Image(
            value=logo,
            format='png',
            width=150
        )

        # Items flex proportionally to the weight
        top_row = [
            header,
            teradata_logo,
         ]
        box_layout = widgets.Layout(display='flex',
                            flex_flow='row',
                            align_items='stretch',
                            width='100%')
        top_row_box = widgets.Box(children=top_row, layout=box_layout)
        
        self.right_pane_tabs = widgets.Tab()
        self._left_pane_ui()
        self.left_pane.layout = widgets.Layout(border_right=_UiImpl._ui_border, padding="10px", width='30%')
        self.right_pane_tabs.layout = widgets.Layout(border_left=_UiImpl._ui_border, padding="10px", width='70%')
        #self.left_pane.layout = border_style
        #self.right_pane_tabs.layout = border_style
        main_layout = widgets.HBox([self.left_pane, self.right_pane_tabs])
        main_layout.layout = widgets.Layout(border="4px solid lightgrey", padding="10px", width='100%')
        #main_layout.layout = widgets.Layout(border="4px solid black", padding="10px")
        self._main_ui = widgets.VBox([top_row_box, main_layout, self.output_widget])

    def _left_pane_ui(self):
        """
        DESCRIPTION:
            Private function that populates the left pane in UI for Vector Store.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        create_button = widgets.Button(icon="plus", tooltip="Create a vector table", layout=widgets.Layout(width="40px"), style={'button_color' : 'transparent'},)
        refresh_button = widgets.Button(icon="refresh", tooltip="Refresh the vector store list", layout=widgets.Layout(width="40px"), style={'button_color' : 'transparent'},)
        use_button = widgets.Button(icon="check-circle", tooltip="Select a vector table from the list below and use it for further operations.", layout=widgets.Layout(width="40px"), style={'button_color' : 'transparent'},)
        health_button = widgets.Button(icon="heartbeat", tooltip="Check vector table Health", layout=widgets.Layout(width="40px"), style={'button_color' : 'transparent'},)
        destroy_button = ConfirmationButton(description='Destroy', icon_name='trash')
        
        self.vector_store_list = widgets.Select(options=[], layout=widgets.Layout(height="250px"))#, description="Vector Stores:")
        
        vs_output_widget = widgets.Output()

        def _on_destroy_click(_):
            """
            DESCRIPTION:
                Private function that is called when the destroy menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            try:
                vs_name = self.vector_store_list.value
                # Check if vs is open in tab
                if vs_name in self.vector_store_objects:
                    # Find in the tabs
                    index = list(self.right_pane_tabs.titles).index(vs_name)

                    # Delete from tabs
                    tab_children = list(self.right_pane_tabs.children)
                    del tab_children[index]
                    titles = list(self.right_pane_tabs.titles)
                    del titles[index]
                    self.right_pane_tabs.children = tab_children
                    self.right_pane_tabs.titles = titles

                    # Delete from stored objects
                    vs_object = self.vector_store_objects[vs_name]
                    del self.vector_store_objects[vs_name]
                else:
                    # VS was not open so get it
                    vs_object = VectorStore(name=vs_name)

                vs_object.destroy()
                
                self.vector_store_list.value = None
                self._refresh_vector_store_list()
                with vs_output_widget:
                    clear_output()
                    print(f"Vector Store {vs_name} destroyed successfully.")
            except Exception as e:
                self.last_error = traceback.format_exc()
                with vs_output_widget:
                    clear_output()
                    print(f"ERROR: {e}")
        
        def _on_create_click(_):
            """
            DESCRIPTION:
                Private function that is called when the create menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            try:
                for i, title in enumerate(self.right_pane_tabs.titles):
                    if title == "Create Vector Store":
                        self.right_pane_tabs.selected_index = i
                        return
                self._add_create_tab()
            except Exception as e:
                self.last_error = traceback.format_exc()

        def _on_refresh_click(_):
            """
            DESCRIPTION:
                Private function that is called when the refresh menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            self._refresh_vector_store_list()

        def _on_health_click(_):
            """
            DESCRIPTION:
                Private function that is called when the health menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            try:
                self._show_display(self._loading_bar, True)
                health_df = VSManager.health()
                self._show_display(self._main_ui, True)
                with self.output_widget:
                    clear_output()
                    IPython.display.display(health_df)
            except Exception as e:
                self._show_display(self._main_ui, True)
                with self.output_widget:
                    clear_output()
                    self.last_error = traceback.format_exc()
                    print(f"ERROR: {e}")

        def _on_use_click(_):
            """
            DESCRIPTION:
                Private function that is called when the use selected menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            selected_vs = self.vector_store_list.value
            if selected_vs:
                self._add_vector_store_tab(selected_vs)
                

        create_button.on_click(_on_create_click)
        refresh_button.on_click(_on_refresh_click)
        health_button.on_click(_on_health_click)
        use_button.on_click(_on_use_click)
        destroy_button.on_click(_on_destroy_click)

        self.left_pane = widgets.VBox([widgets.HBox([create_button, refresh_button, use_button, health_button, destroy_button]), self.vector_store_list])
        self._refresh_vector_store_list()

    def _refresh_vector_store_list(self):
        """
        DESCRIPTION:
            Private function that is called when the refresh is clicked, loading the list of vector tables in the vector store.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            self.vs_df = VSManager.list()
            self.vs_list = self.vs_df.to_pandas()["vs_name"].tolist()
            self.vector_store_list.options = self.vs_list
        except Exception as e:
            with self.output_widget:
                clear_output()
                self.last_error = traceback.format_exc()
                print(f"ERROR: {e}")

    def _add_create_tab(self):
        """
        DESCRIPTION:
            Private function that adds the output of create button to the right pane in UI for Vector Store.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        tab_name = "Create Vector Store"
        if tab_name not in self.right_pane_tabs.children:
            create_tab_content = self._create_update_ui()
            self.right_pane_tabs.children += (create_tab_content,)
            self.right_pane_tabs.set_title(len(self.right_pane_tabs.children) - 1, tab_name)
            self.right_pane_tabs.selected_index = len(self.right_pane_tabs.children)-1

    def _create_update_ui(self, ui_type="Create", vs_object=None, vs_name = ""):
        """
        DESCRIPTION:
            Private function that is shared information, including parameter creation, for Create and Update in UI for Vector Store.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        align_kw = {
            "layout": {'width': 'max-content'},
            "style": {'description_width': '150px'}
        }

        update_dict = {}
        if vs_object is not None:
            update_table = vs_object.get_details().to_pandas()
            if update_table.shape[0] > 0:
                first_row = update_table.iloc[0]
                update_dict = first_row.to_dict()
                for key in ['include_patterns', 'exclude_patterns', 'include_objects', 'exclude_objects']:
                    if key in update_dict and update_dict[key] == "[]":
                        update_dict[key] = ""
                if "file_names" in update_dict and type(update_dict["file_names"]) == str:
                    update_dict["file_names"] = json.loads(update_dict["file_names"])
            

        # Set defaults if they dont exist
        for key in _UiImpl._update_default_values:
            default_value = _UiImpl._update_default_values[key]
            if key not in update_dict:
                update_dict[key] = default_value


        status_button = widgets.Button(icon="info-circle", tooltip="Status", layout=widgets.Layout(width="40px"), style={'button_color': 'transparent'})
        
        vector_store_name_input = widgets.Text(
            description="Vector Store Name:",
            tooltip='Specifies the name of the vector store to be created.',
            value = update_dict.get("vs_name",""),
            **align_kw)
        description_input = widgets.Text(
            description="Description:", 
            tooltip='Specifies the description of the vector store.',
            value = update_dict.get("description",""),
            **align_kw)
        target_database_input = widgets.Text(
            description="Target Database:",
            tooltip='Specifies the database name of the table or view to be indexed for vector store.',
            value = update_dict.get("target_database",""),
            **align_kw)
        object_names_input = widgets.Text(
            description="Object Names:", 
            placeholder='(comma-separated)',
            tooltip='Specifies the table name/teradataml DataFrame to be indexed for vector store.',
            value = update_dict.get("object_names",""),
            **align_kw)
        key_columns_input = widgets.Text(
            description="Key Columns:", 
            placeholder='(comma-separated)',
            tooltip='Specifies the names of the key columns to be used for indexing.',
            value = update_dict.get("key_columns", ""),
            **align_kw)
        data_columns_input = widgets.Text(
            description="Data Columns:", 
            placeholder='(comma-separated)',
            tooltip='Specifies the names of the data columns to be used for indexing.',
            value = update_dict["data_columns"],
            **align_kw)
        vector_column_input = widgets.Text(
            description="Vector Column:", 
            tooltip='Specifies the names of the columns to be used for storing the embeddings.',
            value = update_dict["vector_column"],
            **align_kw)

        chunk_size_input = widgets.IntText(
            description="Chunk Size:",
            tooltip='Specifies the size of each chunk when dividing document files into chunks.',
            value = update_dict["chunk_size"],
            **align_kw)
        optimized_chunking_input = widgets.Checkbox(
            description="Optimized Chunking",
            tooltip='Whether an optimized splitting mechanism supplied by Teradata should be used.',
            value = update_dict["optimized_chunking"],
            **align_kw)
        header_height_input = widgets.IntText(
            description="Header Height:",
            tooltip='Specifies the height (in points) of the header section of a PDF document to be trimmed before processing the main content.',
            value = update_dict["header_height"],
            **align_kw)
        footer_height_input = widgets.IntText(
            description="Footer Height:",
            tooltip='Specifies the height (in points) of the footer section of a PDF document to be trimmed before processing the main content.',
            value = update_dict["footer_height"],
            **align_kw)

        embeddings_model_input = widgets.Combobox(
            description="Embeddings Model:",
            placeholder='Type or Select...',
            options=[
                "amazon.titan-embed-text-v1",
                "amazon.titan-embed-image-v1",
                "amazon.titan-embed-text-v2:0",
                "text-embedding-ada-002",
                "text-embedding-3-small",
                "text-embedding-3-large"
            ],
            ensure_option=False,
            tooltip='Specifies the embeddings model to be used for generating the embeddings.',
            value = update_dict["embeddings_model"],
            **align_kw
        )

        embeddings_dims_input = widgets.IntText(
            description="Embeddings Dims:", 
            tooltip='Specifies the number of dimensions to be used for generating the embeddings.',
            value = update_dict["embeddings_dims"],
            **align_kw)

        metric_input = widgets.Dropdown(
            description="Metric:",
            options=["EUCLIDEAN", "COSINE", "DOTPRODUCT"],
            tooltip='Specifies the metric to be used for calculating the distance between the vectors.',
            value = update_dict["metric"],
            **align_kw
        )
        search_algorithm_input = widgets.Dropdown(
            description="Search Algorithm:",
            options=["VECTORDISTANCE", "KMEANS", "HNSW"],
            tooltip='Specifies the algorithm to be used for searching the tables and views relevant to the question.',
            value = update_dict["search_algorithm"],
            **align_kw
        )
        initial_centroids_method_input = widgets.Dropdown(
            description="Centroids Method:",
            options=["RANDOM", "KMEANS++"],
            tooltip='Specifies the algorithm to be used for initializing the centroids when Search Algorithm is KMEANS.',
            value = update_dict["initial_centroids_method"],
            **align_kw
        )
        train_numcluster_input = widgets.IntText(
            description="Train Num Clusters:", 
            tooltip='Specifies the Number of clusters to be trained when "search_algorithm" is KMEANS.',
            value = update_dict["train_numcluster"],
            **align_kw
            )
        max_iternum_input = widgets.IntText(
            description="Max Iterations:", 
            tooltip='Specifies the maximum number of iterations to be run during training when "search_algorithm" is KMEANS.',
            value = update_dict["max_iternum"], 
            **align_kw
            )
        stop_threshold_input = widgets.FloatText(
            description="Stop Threshold:", 
            tooltip='Specifies the threshold value at which training should be stopped when "search_algorithm" is KMEANS.',
            value = update_dict["stop_threshold"],
            **align_kw
            )
        seed_input = widgets.IntText(
            description="Seed:", 
            tooltip='Specifies the seed value to be used for random number generation when "search_algorithm" is KMEANS.',
            value = update_dict["seed"],
            **align_kw
            )
        num_init_input = widgets.IntText(
            description="Num Init:", 
            tooltip='Specifies the number of times the k-means algorithm should run with different initial centroid seeds.',
            value = update_dict["num_init"],
            **align_kw
            )
        top_k_input = widgets.IntText(
            description="Top K:", 
            tooltip='Specifies the number of top clusters to be considered while searching.',
            value = update_dict["top_k"],
            **align_kw
            )
        search_threshold_input = widgets.FloatText(
            description="Search Threshold:", 
            tooltip='Specifies the threshold value to consider for matching tables while searching.',
            value = update_dict["search_threshold"],
            **align_kw
            )
        search_numcluster_input = widgets.IntText(
            description="Search Num Clusters:", 
            tooltip='Specifies the number of clusters to be considered while searching when "search_algorithm" is KMEANS.',
            value = update_dict["search_numcluster"],
            **align_kw
            )

        prompt_input = widgets.Text(
            description="Prompt:", 
            tooltip='Specifies the prompt to be used by language model to generate responses using top matches.',
            value = update_dict["prompt"],
            **align_kw
            )

        chat_completion_model_input = widgets.Combobox(
            description="Chat Model:",
            placeholder='Type or Select...',
            options=[
                "anthropic.claude-3-haiku-20240307-v1:0",
                "anthropic.claude-instant-v1",
                "anthropic.claude-3-5-sonnet-20240620-v1:0",
                "gpt-35-turbo-16k"
            ],
            ensure_option=False,
            tooltip='Specifies the name of the chat completion model to be used for generating text responses.',
            value = update_dict["chat_completion_model"],
            **align_kw
        )
        document_files_upload = widgets.FileUpload(
            accept='.pdf',
            multiple=True,
            description='Add Document:',
            tooltip='Specifies the input dataset in document files format.',
            **align_kw
        )
        document_files_input_list = widgets.SelectMultiple(
            description="Files:", 
            options=update_dict["file_names"] or [],
            value=update_dict["file_names"] or [],
            layout={'width': '300px'},
            style={'description_width': '150px'})

        ef_search_input = widgets.IntText(
            description="EF Search:",  
            tooltip='Specifies the number of neighbors to be considered during search in HNSW graph.',
            value = update_dict["ef_search"],
            **align_kw
            )
        num_layer_input = widgets.IntText(
            description="Num Layer:", 
            tooltip='Specifies the maximum number of layers for the HNSW graph.',
            value = update_dict["num_layer"],
            **align_kw
            )
        ef_construction_input = widgets.IntText(
            description="EF Construction:", 
            tooltip='Specifies the number of neighbors to be considered during construction of the HNSW graph.',
            value = update_dict["ef_construction"],
            **align_kw
            )
        num_connpernode_input = widgets.IntText(
            description="Connections/Node:", 
            tooltip='Specifies the number of connections per node in the HNSW graph during construction.',
            value = update_dict["num_connpernode"],
            **align_kw
            )
        maxnum_connpernode_input = widgets.IntText(
            description="Max Connections/Node:", 
            tooltip='Specifies the maximum number of connections per node in the HNSW graph during construction.',
            value = update_dict["maxnum_connpernode"],
            **align_kw
            )
        apply_heuristics_input = widgets.Checkbox(
            description="Apply Heuristics", 
            tooltip='Specifies whether to apply heuristics optimizations during construction of the HNSW graph.',
            value = update_dict["apply_heuristics"],
            **align_kw
            )
        include_objects_input = widgets.Text(
            description="Include Objects:", 
            placeholder='(comma-separated)',
            tooltip='Specifies the list of tables and views included in the metadata-based vector store.',
            value = update_dict["include_objects"],
            **align_kw
            )
        exclude_objects_input = widgets.Text(
            description="Exclude Objects:", 
            placeholder='(comma-separated)',
            tooltip='Specifies the list of tables and views excluded from the metadata-based vector store.',
            value = update_dict["exclude_objects"],
            **align_kw
            )
        sample_size_input = widgets.IntText(
            description="Sample Size:", 
            tooltip='Specifies the number of rows to sample from tables and views for the metadata-based vector store embeddings.',
            value = update_dict["sample_size"],
            **align_kw
            )
        rerank_weight_input = widgets.FloatText(
            description="Rerank Weight:", 
            tooltip='Specifies the weight to be used for reranking the search results. Applicable range is 0.0 to 1.0.',
            value = update_dict["rerank_weight"],
            **align_kw
            )
        relevance_top_k_input = widgets.IntText(
            description="Relevance Top K:", 
            tooltip='Specifies the number of top similarity matches to be considered for reranking. Applicable range is 1 to 1024.',
            value = update_dict["relevance_top_k"],
            **align_kw
            )
        relevance_search_threshold_input = widgets.FloatText(
            description="Relevance Threshold:", 
            tooltip='Specifies the threshold value to consider matching tables/views while reranking. A higher threshold value limits responses to the top matches only.',
            value = update_dict["relevance_search_threshold"],
            **align_kw
            )
        include_patterns_input = widgets.Text(
            description="Include Patterns:",
            placeholder='(comma-separated)',
            tooltip='Specifies the list of patterns to be included in the metadata-based vector store.',
            value = update_dict["include_patterns"],
            **align_kw
            )
        exclude_patterns_input = widgets.Text(
            description="Exclude Patterns:", 
            placeholder='(comma-separated)',
            tooltip='Specifies the list of patterns to be excluded from the metadata-based vector store.',
            value = update_dict["exclude_patterns"],
            **align_kw
            )
        ignore_embedding_errors_input = widgets.Checkbox(
            description="Ignore Embedding Errors", 
            tooltip='Specifies whether to ignore errors during embedding generation. Applicable only for AWS.',
            value = update_dict["ignore_embedding_errors"],
            **align_kw
            )

        chat_completion_max_tokens_input = widgets.IntText(
            description="Max Tokens:",
            tooltip='Specifies the maximum number of tokens to be generated by the chat completion model.',
            value = update_dict["chat_completion_max_tokens"],
            **align_kw
            )
        embeddings_base_url_input = widgets.Text(
            description="Embeddings Base URL:", 
            tooltip='Specifies the base URL for the service which is used for generating embeddings.',
            value = update_dict["embeddings_base_url"],
            **align_kw
            )
        completions_base_url_input = widgets.Text(
            description="Completions Base URL:", 
            tooltip='Specifies the base URL for the service which is used for generating completions.',
            value = update_dict["completions_base_url"],
            **align_kw
            )
        ranking_url_input = widgets.Text(
            description="Ranking URL:", 
            tooltip='Specifies the URL for the service which is used for reranking.',
            value = update_dict["ranking_url"],
            **align_kw
            )
        ingest_host_input = widgets.Text(
            description="Ingest Host:", 
            tooltip='Specifies the HTTP host to be used for document parsing.',
            value = update_dict["ingest_host"],
            **align_kw
            )
        ingest_port_input = widgets.IntText(
            description="Ingest Port:", 
            tooltip='Specifies the port to be used for document parsing.',
            value = update_dict["ingest_port"],
            **align_kw
            )
        time_zone_input = widgets.Text(
            description="Time Zone:", 
            tooltip="User's time zone.",
            value = update_dict["time_zone"],
            **align_kw
            )
        nv_ingestor_input = widgets.Checkbox(
            description="NV Ingestor",
            tooltip='Whether to use NVIDIA NV-Ingest for processing the document files.',
            value = update_dict["nv_ingestor"],
            **align_kw)
        extract_text_input = widgets.Checkbox(
            description="Extract Text",
            tooltip='Whether to extract text from the document files when using NVIDIA NV-Ingest.',
            value = update_dict["extract_text"],
            **align_kw)
        extract_images_input = widgets.Checkbox(
            description="Extract Images",
            tooltip='Whether to extract images from the document files when using NVIDIA NV-Ingest.',
            value = update_dict["extract_images"],
            **align_kw)
        extract_tables_input = widgets.Checkbox(
            description="Extract Tables",
            tooltip='Whether to extract tables from the document files when using NVIDIA NV-Ingest.',
            value = update_dict["extract_tables"],
            **align_kw)
        extract_infographics_input = widgets.Checkbox(
            description="Extract Infographics",
            tooltip='Whether to extract infographics from the document files when using NVIDIA NV-Ingest.',
            value = update_dict["extract_infographics"],
            **align_kw)
        extract_method_input = widgets.Dropdown(
            description="Extract Method",
            options=["pdfium", "nemoretriever_parse"],
            tooltip='Method to be used for extracting text from the document files when using NVIDIA NV-Ingest.',
            value = update_dict["extract_method"],
            **align_kw)
        display_metadata_input = widgets.Checkbox(
            description="Display Metadata",
            tooltip='Whether to display metadata describing objects extracted from the document files when using NVIDIA NV-Ingest.',
            value = update_dict["display_metadata"],
            **align_kw)
        tokenizer_input = widgets.Text(
            description="Tokenizer",
            tooltip='Tokenizer to be used for splitting the text into chunks. Applicable only for NVIDIA NV-Ingest.',
            value = update_dict["tokenizer"],
            **align_kw)
        hf_access_token_input = widgets.Text(
            description="HF Access Token:", 
            tooltip='Hugging Face access token to be used for accessing the tokenizer. Applicable only for NVIDIA NV-Ingest.',
            value = update_dict["hf_access_token"],
            **align_kw)
        is_embedded_input = widgets.Checkbox(
            description="Embedded",
            tooltip='Whether the input contains the embedding.',
            value = update_dict["is_embedded"],
            **align_kw)
        is_normalized_input = widgets.Checkbox(
            description="Normalized",
            tooltip='Whether the input contains the normalized embedding.',
            value = update_dict["is_normalized"],
            **align_kw)
        alter_operation_input = widgets.Dropdown(
            description="Alter Operation",
            options=["ADD", "DELETE"],
            tooltip='Specifies the type of operation to be performed while adding new data or deleting existing data from the vector store.',
            value = update_dict["alter_operation"],
            **align_kw)
        update_style_input = widgets.Dropdown(
            description="Update Style",
            options=["MINOR", "MAJOR"],
            tooltip='Specifies the style to be used for "alter_operation" of the data from the vector store when "search_algorithm" is KMEANS/HNSW.',
            value = update_dict["update_style"],
            **align_kw)

        def _on_algorithm_change(_):
            """
            DESCRIPTION:
                Private function that is called when a search algorithm is selected in UI for Vector Store, accordingly certain parameters will be hidden.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            if search_algorithm_input.value == "KMEANS":
                initial_centroids_method_input.layout.display = None
                train_numcluster_input.layout.display = None
                max_iternum_input.layout.display = None
                stop_threshold_input.layout.display = None
                seed_input.layout.display = None
                num_init_input.layout.display = None
                search_numcluster_input.layout.display = None
                search_threshold_input.layout.display = None
                ef_search_input.layout.display = "none"
                num_layer_input.layout.display = "none"
                ef_construction_input.layout.display = "none"
                num_connpernode_input.layout.display = "none"
                maxnum_connpernode_input.layout.display = "none"
                apply_heuristics_input.layout.display = "none"
                
            elif search_algorithm_input.value == "VECTORDISTANCE":
                ef_search_input.layout.display = "none"
                num_layer_input.layout.display = "none"
                ef_construction_input.layout.display = "none"
                num_connpernode_input.layout.display = "none"
                maxnum_connpernode_input.layout.display = "none"
                apply_heuristics_input.layout.display = "none"
                search_threshold_input.layout.display = None
                initial_centroids_method_input.layout.display = "none"
                train_numcluster_input.layout.display = "none"
                max_iternum_input.layout.display = "none"
                stop_threshold_input.layout.display = "none"
                seed_input.layout.display = "none"
                num_init_input.layout.display = "none"
                search_numcluster_input.layout.display = "none"
                
            elif search_algorithm_input.value == "HNSW":
                ef_search_input.layout.display = None
                num_layer_input.layout.display = None
                ef_construction_input.layout.display = None
                num_connpernode_input.layout.display = None
                maxnum_connpernode_input.layout.display = None
                apply_heuristics_input.layout.display = None
                search_threshold_input.layout.display = "none"
                initial_centroids_method_input.layout.display = "none"
                train_numcluster_input.layout.display = "none"
                max_iternum_input.layout.display = "none"
                stop_threshold_input.layout.display = "none"
                seed_input.layout.display = "none"
                num_init_input.layout.display = "none"
                search_numcluster_input.layout.display = "none"

        _on_algorithm_change(None)

        def _on_upload_change(_):
            """
            DESCRIPTION:
                Private function that is called when a file is uploaded in UI for Vector Store, accordingly certain parameters will be hidden.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            new_documents = [os.path.join(Path.home(), 'Downloads', item['name']) for item in document_files_upload.value if item['name'].endswith(".pdf")]
            document_files_upload.value = ()
            original_documents = list(document_files_input_list.options) 
            all_documents = original_documents + new_documents

            document_files_input_list.options = all_documents
            document_files_input_list.value = []

            enabled = len(document_files_input_list.options) > 0
            
            chunk_size_input.layout.display = None if enabled else "none"
            optimized_chunking_input.layout.display = None if enabled else "none"
            header_height_input.layout.display = None if enabled else "none"
            footer_height_input.layout.display = None if enabled else "none"
            nv_ingestor_input.layout.display = None if enabled else "none"
            extract_text_input.layout.display = None if enabled else "none"
            extract_images_input.layout.display = None if enabled else "none"
            extract_tables_input.layout.display = None if enabled else "none"

            extract_infographics_input.layout.display = None if enabled else "none"
            extract_method_input.layout.display = None if enabled else "none"

            display_metadata_input.layout.display = None if enabled else "none"
            tokenizer_input.layout.display = None if enabled else "none"
            hf_access_token_input.layout.display = None if enabled else "none"

            key_columns_input.layout.display = "none" if enabled else None

        _on_upload_change(None)

        def _on_clear_file_click(_):
            """
            DESCRIPTION:
                Private function that is called when the clear button next to file upload is clicked, which clears the file upload in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            document_files_input_list.value = []
            document_files_input_list.options = []
            _on_upload_change(None)

        def _on_remove_file_click(_):
            """
            DESCRIPTION:
                Private function that is called when the clear button next to file upload is clicked, which clears the file upload in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """

            options = document_files_input_list.options
            remove_documents = document_files_input_list.value
            all_documents = list(document_files_input_list.options)
            document_files_input_list.value = []
            for document in remove_documents:
                all_documents.remove(document)
            document_files_input_list.options = all_documents
            
            _on_upload_change(None)


        def _remove_document_params(vs_kwargs):
            """
            DESCRIPTION:
                Private function that is to remove the parameters that should not be included if its Content based Vector Store.

            PARAMETERS:
                vs_kwargs: 
                    Required Argument. 
                    The vector store kwargs.
                    Type: dict
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            document_parameters = ["document_files", "optimized_chunking", "nv_ingestor", "is_normalized"]
            for document_params in document_parameters:
                if document_params in vs_kwargs:
                    del vs_kwargs[document_params]
            return vs_kwargs

        def _on_create_click(_):
            """
            DESCRIPTION:
                Private function that is called when the create button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            try:
                vs_name = vector_store_name_input.value
                if not vs_name:
                    raise ValueError("Vector Store Name is required.")
                document_files = list(document_files_input_list.options)
                if len(document_files) == 0:
                    document_files = ()

                vs_kwargs = {
                    "description": description_input.value or None,
                    "target_database": target_database_input.value or None,
                    "object_names": object_names_input.value.split(",") if object_names_input.value else None,
                    "key_columns": [ x.strip() for x in key_columns_input.value.split(",") ] if key_columns_input.value else None,
                    "data_columns": [ x.strip() for x in data_columns_input.value.split(",") ] if data_columns_input.value else None,
                    "vector_column": vector_column_input.value or None,
                    "chunk_size": chunk_size_input.value or None,
                    "optimized_chunking": optimized_chunking_input.value,
                    "header_height": header_height_input.value or None,
                    "footer_height": footer_height_input.value or None,
                    "embeddings_model": embeddings_model_input.value or None,
                    "embeddings_dims": embeddings_dims_input.value or None,
                    "metric": metric_input.value or None,
                    "search_algorithm": search_algorithm_input.value or None,
                    "initial_centroids_method": initial_centroids_method_input.value or None,
                    "train_numcluster": train_numcluster_input.value or None,
                    "max_iternum": max_iternum_input.value or None,
                    "stop_threshold": stop_threshold_input.value or None,
                    "seed": seed_input.value or None,
                    "num_init": num_init_input.value or None,
                    "top_k": top_k_input.value or None,
                    "search_threshold": search_threshold_input.value or None,
                    "search_numcluster": search_numcluster_input.value or None,
                    "prompt": prompt_input.value or None,
                    "chat_completion_model": chat_completion_model_input.value or None,
                    "document_files": document_files,
                    "ef_search": ef_search_input.value or None,
                    "num_layer": num_layer_input.value or None,
                    "ef_construction": ef_construction_input.value or None,
                    "num_connpernode": num_connpernode_input.value or None,
                    "maxnum_connpernode": maxnum_connpernode_input.value or None,
                    "apply_heuristics": apply_heuristics_input.value,
                    "include_objects": [ x.strip() for x in include_objects_input.value.split(",") ] if include_objects_input.value else None,
                    "exclude_objects": [ x.strip() for x in exclude_objects_input.value.split(",") ] if exclude_objects_input.value else None,
                    "sample_size": sample_size_input.value or None,
                    "rerank_weight": rerank_weight_input.value or None,
                    "relevance_top_k": relevance_top_k_input.value or None,
                    "relevance_search_threshold": relevance_search_threshold_input.value or None,
                    "include_patterns": [ x.strip() for x in include_patterns_input.value.split(",") ] if include_patterns_input.value else None,
                    "exclude_patterns": [ x.strip() for x in exclude_patterns_input.value.split(",") ] if exclude_patterns_input.value else None,
                    "ignore_embedding_errors": ignore_embedding_errors_input.value,
                    "chat_completion_max_tokens": chat_completion_max_tokens_input.value or None,
                    "embeddings_base_url": embeddings_base_url_input.value or None,
                    "completions_base_url": completions_base_url_input.value or None,
                    "ranking_url": ranking_url_input.value or None,
                    "ingest_host": ingest_host_input.value or None,
                    "ingest_port": ingest_port_input.value or None,
                    "time_zone": time_zone_input.value or None,
                    "nv_ingestor": nv_ingestor_input.value,
                    "extract_text": extract_text_input.value,
                    "extract_images": extract_images_input.value,
                    "extract_tables": extract_tables_input.value,
                    "extract_infographics": extract_infographics_input.value,
                    "extract_method": extract_method_input.value or None,
                    "display_metadata": display_metadata_input.value,
                    "tokenizer": tokenizer_input.value or None,
                    "hf_access_token": hf_access_token_input.value or None,
                    "is_embedded" : is_embedded_input.value,
                    "is_normalized" : is_normalized_input.value
                    
                }
                if len(document_files)==0:
                    vs_kwargs = _remove_document_params(vs_kwargs)

                if search_algorithm_input.value == "VECTORDISTANCE" or search_algorithm_input.value == "KMEANS":
                    del vs_kwargs["apply_heuristics"]

                # iterate over dictionary and remove cases where it hasnt changed from default
                for key in vs_kwargs:
                    value = vs_kwargs[key]
                    if key == "embeddings_model" and value == "":
                        vs_kwargs[key] = "amazon.titan-embed-text-v1"
                    if key == "chat_completion_model" and value == "":
                        vs_kwargs[key] = "anthropic.claude-3-haiku-20240307-v1:0"
                    if value is None:
                        continue
                    if key == "object_names":
                        if len(value) == 1 and len(document_files) == 0:
                            vs_kwargs[key] = DataFrame(value[0])
                        continue
                    if key in update_dict and value == update_dict[key]:
                        vs_kwargs[key] = None
                create_args = {k: v for k, v in vs_kwargs.items() if v is not None}
                vs_object = VectorStore(name=vs_name)
                vs_object.create(**create_args)


                def _on_status_click(_):
                    try:
                        status_df = vs_object.status()
                        with self.output_widget:
                            clear_output()
                            IPython.display.display(status_df)
                    except Exception as e:
                        with self.output_widget:
                            clear_output()
                            self.last_error = traceback.format_exc()
                            print(f"ERROR: {e}")
                status_button.on_click(_on_status_click)

                with self.output_widget:
                    clear_output()
                    print("Vector Store created successfully.")
            except Exception as e:
                with self.output_widget:
                    clear_output()
                    self.last_error = traceback.format_exc()
                    self.callstack = traceback.format_exc()
                    print(f"ERROR: {e}")

        def _on_update_click(_):
            """
            DESCRIPTION:
                Private function that is called when the update menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            try:
                vs_name = vector_store_name_input.value
                if not vs_name:
                    raise ValueError("Vector Store Name is required.")
                document_files = document_files_input_list.options
                if len(document_files) == 0:
                    document_files = ()
                vs_kwargs = {
                    "description": description_input.value or None,
                    "target_database": target_database_input.value or None,
                    "object_names": object_names_input.value.split(",") if object_names_input.value else None,
                    "key_columns": [ x.strip() for x in key_columns_input.value.split(",") ] if key_columns_input.value else None,
                    "data_columns": [ x.strip() for x in data_columns_input.value.split(",") ] if data_columns_input.value else None,
                    "vector_column": vector_column_input.value or None,
                    "chunk_size": chunk_size_input.value or None,
                    "optimized_chunking": optimized_chunking_input.value,
                    "header_height": header_height_input.value or None,
                    "footer_height": footer_height_input.value or None,
                    "embeddings_model": embeddings_model_input.value,
                    "embeddings_dims": embeddings_dims_input.value or None,
                    "metric": metric_input.value or None,
                    "search_algorithm": search_algorithm_input.value or None,
                    "initial_centroids_method": initial_centroids_method_input.value or None,
                    "train_numcluster": train_numcluster_input.value or None,
                    "max_iternum": max_iternum_input.value or None,
                    "stop_threshold": stop_threshold_input.value or None,
                    "seed": seed_input.value or None,
                    "num_init": num_init_input.value or None,
                    "top_k": top_k_input.value or None,
                    "search_threshold": search_threshold_input.value or None,
                    "search_numcluster": search_numcluster_input.value or None,
                    "prompt": prompt_input.value or None,
                    "chat_completion_model": chat_completion_model_input.value or None,
                    "document_files": document_files,
                    "ef_search": ef_search_input.value or None,
                    "num_layer": num_layer_input.value or None,
                    "ef_construction": ef_construction_input.value or None,
                    "num_connpernode": num_connpernode_input.value or None,
                    "maxnum_connpernode": maxnum_connpernode_input.value or None,
                    "apply_heuristics": apply_heuristics_input.value,
                    "include_objects": [ x.strip() for x in include_objects_input.value.split(",") ] if include_objects_input.value else None,
                    "exclude_objects": [ x.strip() for x in exclude_objects_input.value.split(",") ] if exclude_objects_input.value else None,
                    "sample_size": sample_size_input.value or None,
                    "rerank_weight": rerank_weight_input.value or None,
                    "relevance_top_k": relevance_top_k_input.value or None,
                    "relevance_search_threshold": relevance_search_threshold_input.value or None,
                    "include_patterns": [ x.strip() for x in include_patterns_input.value.split(",") ] if include_patterns_input.value else None,
                    "exclude_patterns": [ x.strip() for x in exclude_patterns_input.value.split(",") ] if exclude_patterns_input.value else None,
                    "ignore_embedding_errors": ignore_embedding_errors_input.value,
                    "chat_completion_max_tokens": chat_completion_max_tokens_input.value or None,
                    "embeddings_base_url": embeddings_base_url_input.value or None,
                    "completions_base_url": completions_base_url_input.value or None,
                    "ranking_url": ranking_url_input.value or None,
                    "ingest_host": ingest_host_input.value or None,
                    "ingest_port": ingest_port_input.value or None,
                    "time_zone": time_zone_input.value or None,
                    "nv_ingestor": nv_ingestor_input.value,
                    "extract_text": extract_text_input.value,
                    "extract_images": extract_images_input.value,
                    "extract_tables": extract_tables_input.value,
                    "extract_infographics": extract_infographics_input.value,
                    "extract_method": extract_method_input.value or None,
                    "display_metadata": display_metadata_input.value,
                    "tokenizer": tokenizer_input.value or None,
                    "hf_access_token": hf_access_token_input.value or None,
                    "is_embedded" : is_embedded_input.value,
                    "is_normalized" : is_normalized_input.value,
                    "alter_operation": alter_operation_input.value or None,
                    "update_style": update_style_input.value or None

                }
                if len(document_files)==0:
                    vs_kwargs = _remove_document_params(vs_kwargs)

                if search_algorithm_input.value == "VECTORDISTANCE" or search_algorithm_input.value == "KMEANS":
                    del vs_kwargs["apply_heuristics"]

                # iterate over dictionary and remove cases where it hasnt changed from default
                for key in vs_kwargs:
                    value = vs_kwargs[key]
                    if value is None:
                        continue
                    if key == "object_names" :
                        if len(value) == 1 and len(document_files) == 0:
                            vs_kwargs[key] = DataFrame(value[0])
                        continue
                    if key in update_dict and value == update_dict[key]:
                        vs_kwargs[key] = None
                vs_object = VectorStore(name=vs_name)
                vs_object.update(**{k: v for k, v in vs_kwargs.items() if v is not None})

                def _on_status_click(_):
                    """
                    DESCRIPTION:
                        Private function that is called when the status info button is clicked in UI for Vector Store.

                    PARAMETERS:
                        None.
                    
                    RAISES:
                        None.

                    RETURNS:
                        None.
                    """
                    try:
                        status_df = vs_object.status()
                        with self.output_widget:
                            clear_output()
                            IPython.display.display(status_df)
                    except Exception as e:
                        with self.output_widget:
                            clear_output()
                            self.last_error = traceback.format_exc()
                            print(f"ERROR: {e}")
                status_button.on_click(_on_status_click)

                with self.output_widget:
                    clear_output()
                    print("Vector Store updated successfully.")
            except Exception as e:
                with self.output_widget:
                    clear_output()
                    self.last_error = traceback.format_exc()
                    print(f"ERROR: {e}")

        create_button = widgets.Button(description=ui_type, button_style='success')
        if ui_type == "Update":
            vector_store_name_input.disabled = True
            create_button.on_click(_on_update_click)
        else:
            self._show_display(self._loading_bar, True)
            create_button.on_click(_on_create_click)
            self._show_display(self._main_ui, True)
            with self.output_widget:
                clear_output()

        remove_file_button = widgets.Button(description="Remove", layout=widgets.Layout(width="80px"), tooltip="Remove selected document(s) added to Document File upload.")
        remove_file_button.on_click(_on_remove_file_click)
        clear_file_button = widgets.Button(description="Clear", layout=widgets.Layout(width="80px"), tooltip="Clear all the documents added to Document File upload.")
        clear_file_button.on_click(_on_clear_file_click)

        document_files_upload.observe(_on_upload_change, names='value')
        search_algorithm_input.observe(_on_algorithm_change, names='value')

        # alter operation and update style are specific to Update only
        create_names_widgets = [vector_store_name_input, description_input, target_database_input, object_names_input]
        if ui_type == "Update":
            create_names_widgets.extend([alter_operation_input, update_style_input])
        create_names = widgets.VBox(create_names_widgets)
        create_columns = widgets.VBox([key_columns_input, data_columns_input, vector_column_input])
        create_design = widgets.VBox([widgets.HBox([document_files_upload, remove_file_button, clear_file_button]), document_files_input_list, chunk_size_input, optimized_chunking_input, header_height_input, footer_height_input])
        create_embeddings = widgets.VBox([embeddings_model_input, embeddings_dims_input, is_embedded_input, is_normalized_input])
        #left_algorithms = widgets.VBox([metric_input, search_algorithm_input, initial_centroids_method_input, train_numcluster_input, max_iternum_input, stop_threshold_input, seed_input, num_init_input, top_k_input])
        #right_algorithms = widgets.VBox([search_threshold_input, search_numcluster_input, num_layer_input, ef_search_input, ef_construction_input, num_connpernode_input, maxnum_connpernode_input, apply_heuristics_input])
        create_algorithms = widgets.VBox([metric_input, search_algorithm_input, initial_centroids_method_input, train_numcluster_input, max_iternum_input, stop_threshold_input, seed_input, num_init_input, 
            top_k_input, search_threshold_input, search_numcluster_input, num_layer_input, ef_search_input, ef_construction_input, num_connpernode_input, maxnum_connpernode_input, apply_heuristics_input])
        #create_model = widgets.VBox([delay_jitter_input, delay_exp_base_input, prompt_input, self.p_value_int, chat_completion_model_input, document_files_input])
        #create_hnsw = widgets.VBox([self.ef_search_int, num_layer_input, ef_construction_input, num_connpernode_input, maxnum_connpernode_input, apply_heuristics_input])
        create_model = widgets.VBox([prompt_input, chat_completion_model_input, chat_completion_max_tokens_input])
        
        create_extras = widgets.VBox([include_objects_input, exclude_objects_input, sample_size_input, rerank_weight_input,
                relevance_top_k_input,
                relevance_search_threshold_input,
                include_patterns_input,
                exclude_patterns_input,
                ignore_embedding_errors_input,
                time_zone_input])
        create_nim = widgets.VBox([
                embeddings_base_url_input,
                completions_base_url_input,
                ranking_url_input,
                ingest_host_input,
                ingest_port_input, 
                nv_ingestor_input,
                extract_text_input,
                extract_images_input,
                extract_tables_input,
                extract_infographics_input,
                extract_method_input,
                display_metadata_input,
                tokenizer_input,
                hf_access_token_input])


        create_stack = widgets.Stack([ create_names, create_columns, create_design, create_embeddings, create_algorithms, create_model, create_nim, create_extras], selected_index=0)
        create_stack.layout = widgets.Layout(width='50%', height='100%')

        create_groups=['Names', 'Columns', 'Document Design', 'Embeddings', 'Algorithm', 'Model', 'NIM', 'Extras']
        create_list = widgets.Select(
            options=create_groups,
            value='Names',
            disabled=False, 
            layout=widgets.Layout(width='25%', height='140px')
        )

        def _on_create_list_change(_):
            """
            DESCRIPTION:
                Private function that is called when the list of vector stores have changed in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            create_stack.selected_index = create_groups.index(create_list.value)
        create_list.observe(_on_create_list_change, names='value')

        return widgets.VBox([widgets.HBox([create_button, status_button]), widgets.HBox([create_list, create_stack])  ])
        

    def _add_vector_store_tab(self, vs_name):
        """
        DESCRIPTION:
            Private function that is called when selecting a vector store tab to right pane in UI for Vector Store.

        PARAMETERS:
            vs_name: 
                Required Argument. 
                The name of the vector store.
                Type: str
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        if vs_name not in self.vector_store_objects:
            try:
                vs_object = VectorStore(name=vs_name)
                self.vector_store_objects[vs_name] = vs_object
                vs_tab_content = self._create_vector_store_tab_ui(vs_name, vs_object)
                self.right_pane_tabs.children += (vs_tab_content,)
                self.right_pane_tabs.set_title(len(self.right_pane_tabs.children) - 1, vs_name)
                self.right_pane_tabs.selected_index = len(self.right_pane_tabs.children)-1
                vs_object._tab_index = len(self.right_pane_tabs.children)-1
                
            except Exception as e:
                with self.output_widget:
                    clear_output()
                    self.last_error = traceback.format_exc()
                    print(f"ERROR: {e}")
        else:
            vs_object = self.vector_store_objects[vs_name]
            self.right_pane_tabs.selected_index = vs_object._tab_index


    def _create_vector_store_tab_ui(self, vs_name, vs_object):
        """
        DESCRIPTION:
            Private function that is called to populate the right panel in UI for Vector Store.

        PARAMETERS:
            vs_object:
                Required Argument. 
                The Vector Store object.
                Type: VectorStore()
            vs_name: 
                Required Argument. 
                The name of the vector store.
                Type: str
        
        RAISES:
            None.

        RETURNS:
            UI for right panel including menu buttons (ask, details, authenticate, update, close).
        """
        # Create transparent buttons with icons
        ask_button = widgets.Button(icon="question-circle", tooltip="Ask", layout=widgets.Layout(width="40px"), style={'button_color': 'transparent'})
        details_button = widgets.Button(icon="list-alt", tooltip="Details", layout=widgets.Layout(width="40px"), style={'button_color': 'transparent'})
        authenticate_button = widgets.Button(icon="key", tooltip="Authenticate", layout=widgets.Layout(width="40px"), style={'button_color': 'transparent'})
        update_button = widgets.Button(icon="edit", tooltip="Update", layout=widgets.Layout(width="40px"), style={'button_color': 'transparent'})
        #close_button = ConfirmationButton(description='Close', icon_name='times')
        close_button = widgets.Button(icon="times", tooltip="Close Tab", layout=widgets.Layout(width="40px"),style={'button_color': 'transparent'})
        
        vs_output_widget = widgets.Output()
        current_ui = widgets.VBox()

        # Define button click handlers
        def _on_ask_click(_):
            """
            DESCRIPTION:
                Private function that is called when the ask menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            with vs_output_widget:
                clear_output()
            current_ui.children = [self._create_question_tab(vs_object, vs_name)]

        def _on_details_click(_):
            """
            DESCRIPTION:
                Private function that is called when the details menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            try:
                details_df = self.vs_df.to_pandas()
                details_df = details_df[details_df["vs_name"] == vs_name]
                with vs_output_widget:
                    clear_output()
                    IPython.display.display(details_df)
                current_ui.children = [vs_output_widget]
            except Exception as e:
                with vs_output_widget:
                    clear_output()
                    self.last_error = traceback.format_exc()
                    print(f"ERROR: {e}")

        def _on_authenticate_click(_):
            """
            DESCRIPTION:
                Private function that is called when the authenticate menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            with vs_output_widget:
                clear_output()
            current_ui.children = [self._create_authenticate_tab(vs_object)]

        def _on_update_click(_):
            """
            DESCRIPTION:
                Private function that is called when the update menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            try:
                self._show_display(self._loading_bar, True)
                update_ui = self._create_update_ui(ui_type="Update", vs_object=vs_object, vs_name=vs_name)
                current_ui.children = [update_ui]
                self._show_display(self._main_ui, True)
                with self.output_widget:
                    clear_output()
            except Exception as e:
                self._show_display(self._main_ui, True)
                with self.output_widget:
                    clear_output()
                    self.last_error = traceback.format_exc()
                    print(f"ERROR: {e}")

        def _on_close_click(_):
            """
            DESCRIPTION:
                Private function that is called when the close menu button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            # vs_object.close()
            index = self.right_pane_tabs.selected_index
            tab_children = list(self.right_pane_tabs.children)
            del tab_children[index]
            titles = list(self.right_pane_tabs.titles)
            del titles[index]
            self.right_pane_tabs.children = tab_children
            self.right_pane_tabs.titles = titles
            
            del self.vector_store_objects[vs_name]
            # need to set title to right new name if shifted
            #self._function_tabs.set_title(index=index,title=title)

        # Attach handlers to buttons
        ask_button.on_click(_on_ask_click)
        details_button.on_click(_on_details_click)
        authenticate_button.on_click(_on_authenticate_click)
        update_button.on_click(_on_update_click)
        close_button.on_click(_on_close_click)

        # Arrange buttons in a horizontal layout
        button_bar = widgets.HBox([ask_button, details_button, authenticate_button, update_button, close_button])

        # Display the button bar and the initial UI
        current_ui.children = [self._create_question_tab(vs_object, vs_name)]
        return widgets.VBox([button_bar, current_ui])
        
    def _create_question_tab(self, vs_object, vs_name):
        """
            DESCRIPTION:
                Private function that is called for the ask tab is clicked in UI for Vector Store.

            PARAMETERS:
                vs_object:
                    Required Argument. 
                    The Vector Store object.
                    Type: VectorStore()
                vs_name: 
                    Required Argument. 
                    The name of the vector store.
                    Type: str
            
            RAISES:
                None.

            RETURNS:
                UI for authenticate including user (for username), action (for grant vs revoke), and authhenticate button..
            """
        question_input = widgets.Textarea(description="Question:", layout=widgets.Layout(height="auto", width="auto"))
        prompt_input = widgets.Textarea(description="Prompt:", layout=widgets.Layout(height="auto", width="auto"))
        similarity_checkbox = widgets.Checkbox(description="Similarity Search")
        prepare_checkbox = widgets.Checkbox(description="Prepare Response")
        run_button = widgets.Button(description="Run", disabled=True, button_style='success')

        def _on_question_change(change):
            """
            DESCRIPTION:
                Private function that is called when question changed in UI for Vector Store.

            PARAMETERS:
                change:
                    Required Argument. 
                    Based on the action of entered input to the question box.
                    Type: dict
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            run_button.disabled = not bool(change["new"])

        def _on_similarity_toggle(change):
            """
            DESCRIPTION:
                Private function that is called when similarity search checkbox is clicked in UI for Vector Store.

            PARAMETERS:
                change:
                    Required Argument. 
                    Based on the action of clicking the toggle.
                    Type: dict
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            prompt_input.disabled = change["new"]

        def _on_response_toggle(change):
            """
            DESCRIPTION:
                Private function that is called when prepare response checkbox is clicked in UI for Vector Store.

            PARAMETERS:
                change:
                    Required Argument. 
                    Based on the action of clicking the toggle.
                    Type: dict
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            if change["new"]:
                # when running prepare response, similarity search must also be clicked
                similarity_checkbox.value = True

        def _on_run_click(_):
            """
            DESCRIPTION:
                Private function that is called when the run button is clicked for similarity search/prepare response for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            try:
                self._show_display(self._loading_bar, True)
                update_ui = self._create_update_ui(ui_type="Update", vs_object=vs_object, vs_name=vs_name)
                current_ui.children = [update_ui]
                self._show_display(self._main_ui, True)
                with self.output_widget:
                    clear_output()
            except Exception as e:
                self._show_display(self._main_ui, True)
                with self.output_widget:
                    clear_output()
                    self.last_error = traceback.format_exc()
                    print(f"ERROR: {e}")


            try:
                self._show_display(self._loading_bar, True)
                if similarity_checkbox.value:
                    result = vs_object.similarity_search(question=question_input.value).similar_objects
                    self._recent_similarity_search_result = result
                elif prepare_checkbox.value:
                    if not self._recent_similarity_search_result:
                        raise ValueError("Run similarity search first before running prepare response.")
                    result = vs_object.prepare_response(question=question_input.value, prompt=prompt_input.value, similarity_results=self._recent_similarity_search_result)
                else:
                    result = vs_object.ask(question=question_input.value, prompt=prompt_input.value)
                self._answers[vs_name] = result
                self._show_display(self._main_ui, True)
                with self.output_widget:
                    clear_output()
                    IPython.display.display(result)
            except Exception as e:
                self._show_display(self._main_ui, True)
                with self.output_widget:
                    clear_output()
                    self.last_error = traceback.format_exc()
                    print(f"ERROR: {e}")

        question_input.observe(_on_question_change, names="value")
        similarity_checkbox.observe(_on_similarity_toggle, names="value")
        prepare_checkbox.observe(_on_response_toggle)
        run_button.on_click(_on_run_click)

        return widgets.VBox([question_input, prompt_input, similarity_checkbox, prepare_checkbox, run_button])

    def _create_authenticate_tab(self, vs_object):
        """
        DESCRIPTION:
            Private function that creates the authenticate tab for Vector Store.

        PARAMETERS:
            vs_object:
                Required Argument. 
                The Vector Store object.
                Type: VectorStore()
        
        RAISES:
            None.

        RETURNS:
            UI for authenticate including user (for username), action (for grant vs revoke), and authenticate button.
        """
        user = widgets.Text(description="User Name:", placeholder='Enter user name')
        action = widgets.Dropdown(options=['GRANT', 'REVOKE'], value='GRANT', description='Action:', disabled=False)
        #permission = widgets.Dropdown(options=['READ', 'WRITE'], value='READ', description='Permission:', disabled=False)
        authenticate_button = widgets.Button(description="Authenticate", button_style='success')
        
        def _on_authenticate_click(_):
            """
            DESCRIPTION:
                Private function that is called when authenticate button is clicked in UI for Vector Store.

            PARAMETERS:
                None.
            
            RAISES:
                None.

            RETURNS:
                None.
            """
            try:
                if action.value == "GRANT":
                    vs_object.grant.user(user.value)
                # else revoke
                else:
                    vs_object.revoke.user(user.value)


                with self.output_widget:
                    clear_output()
                    result = vs_object.list_user_permissions()
                    IPython.display.display(result)

            except Exception as e:
                with self.output_widget:
                    clear_output()
                    self.last_error = traceback.format_exc()
                    print(f"ERROR: {e}")

        authenticate_button.on_click(_on_authenticate_click)
        
        return widgets.VBox([user, action, authenticate_button])


    def _create_ui(self):      
        """
        DESCRIPTION:
            Private function that creates the ipywidgets UI for Vector Store.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """         
        
        self._init_ui()

        
    def _open_ui(self):
        """
        DESCRIPTION:
            Private function that opens the teradatamlwidgets Vector Store UI. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._show_display(self._main_ui, False)


    def _get_answer_dataframe(self, vs_name):
        """
        Access the output dataframe.

        PARAMETERS:
            vs_name: 
                Required Argument. 
                The name of the vector store.
                Type: str
                
        EXCEPTIONS:
            None.

        RETURNS: 
            teradataml.DataFrame
        
        EXAMPLE:
            df = ui.get_output_dataframe(0)
        """
        if vs_name not in self._answers:
            return None
        return self._answers[vs_name]

    _update_default_values = {
        "vs_name" : "",
        "description" : "",
        "target_database" : "",
        "object_names" : "",
        "key_columns" : "",
        "data_columns" : "",
        "vector_column" : "vector_index",
        "chunk_size" : 512,
        "optimized_chunking" : True,
        "header_height" : 0,
        "footer_height" : 0,
        "embeddings_model" : "",
        "embeddings_dims" : 0,
        "metric" : "EUCLIDEAN",
        "search_algorithm" : "VECTORDISTANCE",
        "initial_centroids_method" : "RANDOM",
        "train_numcluster" : 0,
        "max_iternum" : 10,
        "stop_threshold" : 0.0395,
        "seed" : 0,
        "num_init" : 1,
        "top_k" : 10,
        "search_threshold" : 0,
        "search_numcluster" : 0,
        "prompt" : "",
        "chat_completion_model" : "",
        "file_names" : (),
        "ef_search" : 32,
        "num_layer" : 0,
        "ef_construction" : 32,
        "num_connpernode" : 32,
        "maxnum_connpernode" : 32,
        "apply_heuristics" : True,
        "include_objects" : None,
        "exclude_objects" : None,
        "sample_size" : 20,
        "rerank_weight" : 0.2,
        "relevance_top_k" : 60,
        "relevance_search_threshold" : 0,
        "include_patterns" : None,
        "exclude_patterns" : None,
        #"batch" : False,
        "ignore_embedding_errors" : False,
        "chat_completion_max_tokens" : 16384,
        "embeddings_base_url" : "",
        "completions_base_url" : "",
        "ranking_url" : "",
        "ingest_host" : "",
        "ingest_port" : 7670,
        "time_zone" : "UTC",
        "nv_ingestor" : False,
        "extract_text" : True,
        "extract_images" : True,
        "extract_tables" : True,
        "extract_infographics": False,
        "extract_method": "pdfium",
        "display_metadata" : False,
        "tokenizer": "meta-llama/Llama-3.2-1B",
        "hf_access_token": None,
        "is_embedded" : False,
        "is_normalized" : False,
        "alter_operation" : "ADD",
        "update_style" : "MINOR"
    }

    _ui_border = "2px solid black"