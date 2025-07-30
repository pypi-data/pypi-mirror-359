# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2025 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: aanchal.kavedia@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

teradatagenai.common.constants
----------
A class for holding all constants
"""
from enum import Enum
from teradataml.options.configure import configure
from teradataml.common.constants import HTTPRequest
from teradataml.common.utils import UtilFuncs
from teradataml.utils.validators import _Validators

class Action(Enum):
    # Holds variable names for the type of grant to be provided.
    GRANT = "GRANT"
    REVOKE = "REVOKE"

class Permission(Enum):
    # Holds variable names for the type of permission to be provided.
    USER = "USER"
    ADMIN = "ADMIN"

class VSApi(Enum):
    # Holds variable names for the type of API to be used.
    Ask = "ask"
    PrepareResponse = "prepare-response"
    SimilaritySearch = "similarity-search"

class VectorStoreURLs:
    # Class to store the vector store URLs
    @property
    def base_url(self):
        return f"{configure._vector_store_base_url}/api/v1/"

    @property
    def session_url(self):
        return f"{self.base_url}session"

    @property
    def vectorstore_url(self):
        return f"{self.base_url}vectorstores"

    @property
    def patterns_url(self):
        return f"{self.base_url}patterns"

class _Authenticate:
    """ Parent class to either grant or revoke access on the vector store. """

    def __init__(self, action, vs):
        """
        DESCRIPTION:
            Method to initialize the _Authenticate class.

        PARAMETERS:
            action:
                Required Arguments.
                Specifies the action to be performed (grant/revoke).
                Type: str

            vs:
                Required Arguments.
                Specifies the vector store object.
                Type: VectorStore
        
        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> _Authenticate(action="GRANT", vs=vs)
        """
        self.action = action
        self.vs = vs
        self.__set_user_permissions_url = "{0}permissions/{1}?user_name={2}&action={3}&permission={4}&log_level={5}"
        # Avoid circular import
        from teradatagenai.vector_store import VSManager
        self._session_header = VSManager._generate_session_id()
        self.__base_url = VectorStoreURLs().base_url

    def _submit_permission_request(self, username, permission):
        """
        DESCRIPTION:
            Internal function to submit the grant/revoke permission request to the vector store.

        PARAMETERS:
            username:
                Required Arguments.
                Specifies the name of the user.
                Type: str
            
            permission:
                Required Arguments.
                Specifies the type of permission to be provided.
                Type: str

        RETURNS:
            HTTP response

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> _Authenticate._submit_permission_request(username="test_user", permission=Permission.ADMIN.value)
        """
        # Validate the username
        arg_info_matrix = []
        arg_info_matrix.append(["username", username, False, (str), True])
        _Validators._validate_function_arguments(arg_info_matrix)

        # HTTP request to grant/revoke USER/ADMIN access to the user
        response = UtilFuncs._http_request(self.__set_user_permissions_url.format(
                                                                                  self.__base_url,
                                                                                  self.vs.name,
                                                                                  username,
                                                                                  self.action,
                                                                                  permission,
                                                                                  self.vs._log),
                                            HTTPRequest.PUT,
                                            headers=self._session_header['vs_header'],
                                            cookies={'session_id': self._session_header['vs_session_id']})
        # Return the response
        return response

    def admin(self, username):
        """
        DESCRIPTION:
            Internal function to provide admin permissions of the
            vector store to the user.

        PARAMETERS:
            username:
                Required Arguments.
                Specifies the name of the user.
                Type: str

        RETURNS:
            None

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> _Authenticate.admin(username="test_user")
        """
        # Submit the grant/revoke ADMIN permission request to the vector store for the user
        response = self._submit_permission_request(username, Permission.ADMIN.value)
        # Process the response
        self.vs._process_vs_response(self.action, response)

    def user(self, username):
        """
        DESCRIPTION:
            Internal function to provide user permissions to the vector store.

        PARAMETERS:
            username:
                Required Arguments.
                Specifies the name of the user.
                Type: str

        RETURNS:
            None

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> _Authenticate.user(username="test_user")
        """
        # Submit the grant/revoke USER permission request to the vector store for the user
        response = self._submit_permission_request(username, Permission.USER.value)
        # Process the response
        self.vs._process_vs_response(self.action, response)

class _Grant(_Authenticate):
    """ Class to grant access to the vector store."""
    def __init__(self, vs):
        super().__init__(Action.GRANT.value, vs)

class _Revoke(_Authenticate):
    """ Class to revoke access to the vector store."""
    def __init__(self, vs):
        super().__init__(Action.REVOKE.value, vs)

# Dict to map the python variable names of vs_parameters to REST variable names.
VSParameters = {
    "description": "description",
    "embeddings_model": "embeddings_model",
    "embeddings_dims": "embeddings_dims",
    "metric": "metric",
    "search_algorithm": "search_algorithm",
    "top_k": "top_k",
    "initial_centroids_method": "initial_centroids_method",
    "train_numcluster": "train_numcluster",
    "max_iternum": "max_iternum",
    "stop_threshold": "stop_threshold",
    "seed": "seed",
    "num_init": "num_init",
    "search_threshold": "search_threshold",
    "search_numcluster": "search_numcluster",
    "prompt": "prompt",
    "chat_completion_model": "chat_completion_model",
    "ef_search": "ef_search",
    "num_layer": "num_layer",
    "ef_construction": "ef_construction",
    "num_connpernode": "num_connPerNode",
    "maxnum_connpernode": "maxNum_connPerNode",
    "apply_heuristics": "apply_heuristics",
    "rerank_weight": "rerank_weight",
    "relevance_top_k": "relevance_top_k",
    "relevance_search_threshold": "relevance_search_threshold",
    "time_zone": "time_zone",
    "ignore_embedding_errors": "ignore_embedding_errors",
    "chat_completion_max_tokens": "chat_completion_max_tokens",
    "completions_base_url": "base_url_completions",
    "embeddings_base_url": "base_url_embeddings",
    "ingest_host": "doc_ingest_host",
    "ingest_port": "doc_ingest_port"
}

# Dict to map the python variable names of vs_index to REST variable names.
VSIndex = {
    "target_database": "target_database",
    "object_names": "object_names",
    "key_columns": "key_columns",
    "data_columns": "data_columns",
    "vector_column": "vector_column",
    "chunk_size": "chunk_size",
    "optimized_chunking": "optimized_chunking",
    "is_embedded": "is_embedded",
    "is_normalized": "is_normalized",
    "header_height": "header_height",
    "footer_height": "footer_height",
    "include_objects": "include_objects",
    "exclude_objects": "exclude_objects",
    "include_patterns": "include_patterns",
    "exclude_patterns": "exclude_patterns",
    "sample_size": "sample_size",
    "alter_operation": "alter_operation",
    "update_style": "update_style",
    "nv_ingestor": "nv_ingestor",
    "display_metadata": "display_metadata",
    "extract_text": "extract_text",
    "extract_images": "extract_images",
    "extract_tables": "extract_tables",
    "extract_method": "extract_method",
    "tokenizer": "tokenizer",
    "extract_infographics": "extract_infographics",
    "hf_access_token": "hf_access_token"
}

# Dict to map the python variable names of vs_parameters to REST variable names.
SimilaritySearchParams = {
    "data": "input_table",
    "column": "input_query_column",
    "question": "question_vector"
}

