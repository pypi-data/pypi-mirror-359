import json
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import loguru

from ..constants import DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from ..logs import configure_logging, set_correlation_id
from ..types._api_version import ApiVersion
from ..types._request_data import RequestData


class AiriaBaseClient:
    """Base client containing shared functionality for Airia API clients."""

    openai = None
    anthropic = None

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
    ):
        """
        Initialize the Airia API client base class.

        Args:
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            bearer_token: Bearer token for authentication. Must be provided explicitly (no environment variable fallback).
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
        """
        # Resolve authentication credentials
        self.api_key, self.bearer_token = self.__class__._resolve_auth_credentials(
            api_key, bearer_token
        )

        # Store configuration
        self.base_url = base_url
        self.timeout = timeout
        self.log_requests = log_requests

        # Initialize logger
        self.logger = configure_logging() if custom_logger is None else custom_logger

    @staticmethod
    def _resolve_auth_credentials(
        api_key: Optional[str] = None, bearer_token: Optional[str] = None
    ):
        """
        Resolve authentication credentials from parameters and environment variables.

        Args:
            api_key (Optional[str]): The API key provided as a parameter. Defaults to None.
            bearer_token (Optional[str]): The bearer token provided as a parameter. Defaults to None.

        Returns:
            tuple: (api_key, bearer_token) - exactly one will be non-None

        Raises:
            ValueError: If no authentication method is provided or if both are provided.
        """
        # Check for explicit conflict first
        if api_key and bearer_token:
            raise ValueError(
                "Cannot provide both api_key and bearer_token. Please use only one authentication method."
            )

        # If bearer token is explicitly provided, use it exclusively
        if bearer_token:
            return None, bearer_token

        # If API key is explicitly provided, use it exclusively
        if api_key:
            return api_key, None

        # If neither is provided explicitly, fall back to environment variable
        resolved_api_key = os.environ.get("AIRIA_API_KEY")
        if resolved_api_key:
            return resolved_api_key, None

        # No authentication method found
        raise ValueError(
            "Authentication required. Provide either api_key (or set AIRIA_API_KEY environment variable) or bearer_token."
        )

    def _prepare_request(
        self,
        url: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """
        Prepare request data including headers, authentication, and logging.
        
        This method sets up all the necessary components for an API request including
        correlation ID, authentication headers, and sanitized logging.
        
        Args:
            url: The target URL for the request
            payload: Optional JSON payload for the request body
            params: Optional query parameters for the request
            correlation_id: Optional correlation ID for request tracing
            
        Returns:
            RequestData: A data structure containing all prepared request components
        """
        # Set correlation ID if provided or generate a new one
        correlation_id = set_correlation_id(correlation_id)

        # Set up base headers
        headers = {
            "X-Correlation-ID": correlation_id,
            "Content-Type": "application/json",
        }

        # Add authentication header based on the method used
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        elif self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        # Log the request if enabled
        if self.log_requests:
            # Create a sanitized copy of headers and params for logging
            log_headers = headers.copy()
            log_params = params.copy() if params is not None else {}

            # Filter out sensitive headers
            if "X-API-KEY" in log_headers:
                log_headers["X-API-KEY"] = "[REDACTED]"
            if "Authorization" in log_headers:
                log_headers["Authorization"] = "[REDACTED]"

            # Process payload for logging
            log_payload = payload.copy() if payload is not None else {}
            if "images" in log_payload and log_payload["images"] is not None:
                log_payload["images"] = f"{len(log_payload['images'])} images"
            if "files" in log_payload and log_payload["files"] is not None:
                log_payload["files"] = f"{len(log_payload['files'])} files"
            log_payload = json.dumps(log_payload)

            self.logger.info(
                f"API Request: POST {url}\n"
                f"Headers: {json.dumps(log_headers)}\n"
                f"Payload: {log_payload}"
                f"Params: {json.dumps(log_params)}\n"
            )

        return RequestData(
            **{
                "url": url,
                "payload": payload,
                "headers": headers,
                "params": params,
                "correlation_id": correlation_id,
            }
        )

    def _pre_execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: bool = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: bool = False,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V2.value,
    ):
        """
        Prepare request data for pipeline execution endpoint.
        
        This internal method constructs the URL and payload for pipeline execution
        requests, validating the API version and preparing all request components.
        
        Args:
            pipeline_id: ID of the pipeline to execute
            user_input: Input text to process
            debug: Whether to enable debug mode
            user_id: Optional user identifier
            conversation_id: Optional conversation identifier
            async_output: Whether to enable streaming output
            include_tools_response: Whether to include tool responses
            images: Optional list of base64-encoded images
            files: Optional list of base64-encoded files
            data_source_folders: Optional data source folder configuration
            data_source_files: Optional data source files configuration
            in_memory_messages: Optional list of in-memory messages
            current_date_time: Optional current date/time in ISO format
            save_history: Whether to save to conversation history
            additional_info: Optional additional information
            prompt_variables: Optional prompt variables
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request
            
        Returns:
            RequestData: Prepared request data for the pipeline execution endpoint
            
        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self.base_url, f"{api_version}/PipelineExecution/{pipeline_id}")

        payload = {
            "userInput": user_input,
            "debug": debug,
            "userId": user_id,
            "conversationId": conversation_id,
            "asyncOutput": async_output,
            "includeToolsResponse": include_tools_response,
            "images": images,
            "files": files,
            "dataSourceFolders": data_source_folders,
            "dataSourceFiles": data_source_files,
            "inMemoryMessages": in_memory_messages,
            "currentDateTime": current_date_time,
            "saveHistory": save_history,
            "additionalInfo": additional_info,
            "promptVariables": prompt_variables,
        }

        request_data = self._prepare_request(
            url=url, payload=payload, correlation_id=correlation_id
        )

        return request_data

    def _pre_get_projects(
        self,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for getting projects endpoint.
        
        Args:
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request
            
        Returns:
            RequestData: Prepared request data for the projects endpoint
            
        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self.base_url, f"{api_version}/Project/paginated")
        request_data = self._prepare_request(url, correlation_id=correlation_id)

        return request_data

    def _pre_get_active_pipelines_ids(
        self,
        project_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for getting active pipelines IDs.
        
        Args:
            project_id: ID of the project to get configuration for
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request
            
        Returns:
            RequestData: Prepared request data for the pipeline config endpoint
            
        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self.base_url, f"{api_version}/PipelinesConfig")
        params = {"projectId": project_id} if project_id is not None else None
        request_data = self._prepare_request(
            url, params=params, correlation_id=correlation_id
        )

        return request_data

    def _pre_get_pipeline_config(
        self,
        pipeline_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for getting pipeline configuration endpoint.
        
        Args:
            pipeline_id: ID of the pipeline to get configuration for
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request
            
        Returns:
            RequestData: Prepared request data for the pipeline config endpoint
            
        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self.base_url, f"{api_version}/PipelinesConfig/export/{pipeline_id}"
        )
        request_data = self._prepare_request(url, correlation_id=correlation_id)

        return request_data

    def _pre_create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
        deployment_id: Optional[str] = None,
        data_source_files: Dict[str, Any] = {},
        is_bookmarked: bool = False,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for creating a new conversation.
        
        This internal method constructs the URL and payload for conversation creation
        requests, including all conversation metadata and settings.
        
        Args:
            user_id: ID of the user creating the conversation
            title: Optional title for the conversation
            deployment_id: Optional deployment to associate with the conversation
            data_source_files: Optional data source files configuration
            is_bookmarked: Whether the conversation should be bookmarked
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request
            
        Returns:
            RequestData: Prepared request data for the conversation creation endpoint
            
        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self.base_url, f"{api_version}/Conversations")

        payload = {
            "userId": user_id,
            "title": title,
            "deploymentId": deployment_id,
            "dataSourceFiles": data_source_files,
            "isBookmarked": is_bookmarked,
        }

        request_data = self._prepare_request(
            url=url, payload=payload, correlation_id=correlation_id
        )

        return request_data

    def _pre_get_conversation(
        self,
        conversation_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for retrieving a conversation by ID.
        
        This internal method constructs the URL for conversation retrieval
        requests using the provided conversation identifier.
        
        Args:
            conversation_id: ID of the conversation to retrieve
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request
            
        Returns:
            RequestData: Prepared request data for the conversation retrieval endpoint
            
        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self.base_url, f"{api_version}/Conversations/{conversation_id}")
        request_data = self._prepare_request(url, correlation_id=correlation_id)

        return request_data

    def _pre_delete_conversation(
        self,
        conversation_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for deleting a conversation by ID.
        
        This internal method constructs the URL for conversation deletion
        requests using the provided conversation identifier.
        
        Args:
            conversation_id: ID of the conversation to delete
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request
            
        Returns:
            RequestData: Prepared request data for the conversation deletion endpoint
            
        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self.base_url, f"{api_version}/Conversations/{conversation_id}")
        request_data = self._prepare_request(url, correlation_id=correlation_id)

        return request_data
