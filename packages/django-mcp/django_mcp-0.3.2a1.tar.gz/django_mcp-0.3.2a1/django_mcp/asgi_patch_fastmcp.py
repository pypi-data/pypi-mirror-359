"""
django_mcp/asgi_patch_fastmcp.py

Patches FastMCP.sse_app to handle dynamic paths and ASGI connection details
"""

import asyncio
import collections
import contextvars
import json
import typing

from django.conf import settings
from django.core.cache import cache
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request

from .log import logger
from .interop_django_fastapi import _interpolate_starlette_path_with_url_params
from .asgi_interceptors import make_intercept_sse_send
from .mcp_sdk_session_replay import SseReadStreamProxy

# Context variable to store MCP path parameters captured during the ASGI SSE connection
mcp_connection_path_params: contextvars.ContextVar[dict[str, typing.Any] | None] = contextvars.ContextVar(
    "mcp_connection_path_params", default=None
)


class SsePatchedApp:
    """
    ASGI application to handle SSE connections with dynamic path parameters
    and message URL rewriting.
    """

    def __init__(self, mcp_server_instance: FastMCP, starlette_base_path: str, sse_transport: SseServerTransport, should_cache_sessions: bool):
        self._mcp_server_instance = mcp_server_instance
        self._starlette_base_path = starlette_base_path
        self._sse_transport = sse_transport
        self._should_cache_sessions = should_cache_sessions

    async def __call__(self, scope, receive, send):
        request = Request(scope, receive=receive)

        token = None  # Initialize token for context variable reset
        resolved_base_url_from_params = "" # Initialize to avoid potential UnboundLocalError in error logs
        request_path = scope.get("path", "unknown_path")

        if settings.MCP_LOG_HTTP_HEADERS_ON_SSE_CONNECT:
            logger.info(f'SSE connection headers for {request_path}:')
            for header_key, header_value in scope.get("headers", []):
                logger.info(f'\t{header_key.decode()}: {header_value.decode()}')

        # Step 1) Capture path parameters from the request and store them in Context
        try:
            # Extract path parameters from the request
            path_params = request.path_params

            # Calculate the actual base URL using the captured parameters
            resolved_base_url_from_params = _interpolate_starlette_path_with_url_params(
                self._starlette_base_path, path_params
            )
            logger.info(f"Resolved base URL for SSE: {resolved_base_url_from_params}")

            # Set the context variable for the duration of this connection
            # so that URL params can be accessed by mcp.tool-decorated functions
            token = mcp_connection_path_params.set(path_params)
            logger.debug(f"Set mcp_connection_path_params: {path_params}")
        except Exception as e:
            logger.exception(f"Error processing path parameters or setting context var: {e}")
            # Reset context var if set before error occurred during setup
            if token:
                mcp_connection_path_params.reset(token)
            await send({'type': 'http.response.start', 'status': 500, 'headers': [[b'content-type', b'text/plain']]})
            await send({'type': 'http.response.body', 'body': b'Error setting up SSE connection.', 'more_body': False})
            raise # Re-raise the exception

        # Step 2) Intercept the original ASGI send callable to be able to rewrite SSE payloads
        intercepted_send = make_intercept_sse_send(
            self._sse_transport,
            send,
            resolved_base_url_from_params
        )
        try:
            # Use the intercepted send when connecting
            async with self._sse_transport.connect_sse(
                scope,
                receive,
                intercepted_send,
            ) as (read_stream, write_stream):
                # Wrap read_stream in proxy to intercept messages, passing caching flag
                read_stream_proxied = SseReadStreamProxy(
                    read_stream,
                    resolved_base_url_from_params,
                    enable_cache_persist_sessions=self._should_cache_sessions
                )
            # Run the MCP server loop
                await self._mcp_server_instance._mcp_server.run(
                    read_stream_proxied,
                    write_stream,
                    self._mcp_server_instance._mcp_server.create_initialization_options(),
                )
                logger.info(f"MCP server run completed for SSE connection ({request_path}).")
        except Exception as e:
            logger.exception(f"Error during SSE connection or MCP server run for {request_path}: {e}")
        finally:
            # Ensure the context variable is reset when the connection closes
            if token:
                mcp_connection_path_params.reset(token)
                logger.debug("Reset mcp_connection_path_params")
            logger.info(f"SseEndpointApp.__call__: FINISHING for path: {request_path}")


# Override FastMCP.sse_app() to support nested paths (e.g. /mcp/sse instead of /sse)
# This monkey patch addresses a limitation in modelcontextprotocol/python-sdk.
# Related issue: https://github.com/modelcontextprotocol/python-sdk/issues/412
# Source code reference (original method):
# https://github.com/modelcontextprotocol/python-sdk/blob/70115b99b3ee267ef10f61df21f73a93db74db03/src/mcp/server/fastmcp/server.py#L480
def FastMCP_sse_app_patch(_self: FastMCP, starlette_base_path: str, *, enable_cache_persist_sessions: bool = True):
    '''
    Patched version of FastMCP.sse_app

    Initializes the SseServerTransport and provides a custom `handle_sse`
    ASGI endpoint that captures path parameters, stores them in Context,
    and intercepts the outgoing SSE 'endpoint' event to inject the correctly
    resolved message posting URL.
    '''

    # Only enable caching if the path is dynamic AND caching is enabled by config
    is_dynamic_path = "{" in starlette_base_path
    should_cache_sessions = is_dynamic_path and enable_cache_persist_sessions
    logger.info(
        f"Dynamic path detected: {is_dynamic_path}, Caching enabled by config: {enable_cache_persist_sessions}, Session caching active: {should_cache_sessions}"
    )

    # Initialize SseServerTransport - message URL here is just a template
    sse_transport = SseServerTransport(f'{starlette_base_path}/messages/')

    sse_app_handler = SsePatchedApp(
        mcp_server_instance=_self,
        starlette_base_path=starlette_base_path,
        sse_transport=sse_transport,
        should_cache_sessions=should_cache_sessions
    )

    # Return the handler and transport instance
    return (sse_app_handler, sse_transport)
