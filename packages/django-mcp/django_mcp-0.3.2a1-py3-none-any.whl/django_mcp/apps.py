"""
django_mcp/apps.py

Django AppConfig for django_mcp
"""

from django.apps import AppConfig
from django.conf import settings
from django_mcp import mcp_app
from .loader import register_mcp_modules
from .log import logger, configure_logging
# Ensure both patches are imported correctly
from .mcp_sdk_patches import patch_mcp_tool_decorator, patch_mcp_get_context

class MCPConfig(AppConfig):
    name = 'django_mcp'
    verbose_name = 'Django MCP'

    defaults = {
        "MCP_BASE_URL": "",
        "MCP_LOG_LEVEL": "INFO",
        'MCP_LOG_TOOL_REGISTRATION': True,
        'MCP_LOG_TOOL_DESCRIPTIONS': False,
        'MCP_LOG_HTTP_HEADERS_ON_SSE_CONNECT': True,
        'MCP_SERVER_INSTRUCTIONS': 'Provides MCP tools',
        "MCP_SERVER_TITLE": "Django MCP Server",
        'MCP_SERVER_VERSION': '0.1.0',
        'MCP_DIRS': [],
        "MCP_PATCH_SDK_TOOL_LOGGING": True,
        "MCP_PATCH_SDK_GET_CONTEXT": True,
        
        # HTTP Stateless Transport Settings
        'MCP_HTTP_TRANSPORT_ENABLED': False,
        'MCP_HTTP_REQUEST_TIMEOUT': 30.0,
        'MCP_HTTP_MAX_REQUEST_SIZE': 10 * 1024 * 1024,  # 10MB
        'MCP_HTTP_ENABLE_COMPRESSION': True,
        'MCP_HTTP_CORS_ENABLED': False,
        'MCP_HTTP_CORS_ORIGINS': [],
        'MCP_HTTP_CORS_METHODS': ["GET", "POST", "OPTIONS"],
        'MCP_HTTP_CORS_HEADERS': ["Content-Type", "Authorization"],
        'MCP_HTTP_JSON_RESPONSE': False,
        'MCP_HTTP_HEALTH_CHECK_ENABLED': True,
        'MCP_HTTP_HEALTH_CHECK_PATH': "/health",
        'MCP_HTTP_ENABLE_METRICS': False,
        'MCP_HTTP_METRICS_PATH': "/metrics",
        'MCP_HTTP_SESSION_TTL': 3600,  # 1 hour
        'MCP_HTTP_SESSION_CLEANUP_INTERVAL': 300,  # 5 minutes
    }

    def apply_default_settings(self):
        """Applies default settings if they are not present in Django's settings."""
        for key, value in self.defaults.items():
            if not hasattr(settings, key):
                setattr(settings, key, value)

    def ready(self):
        """Called when the Django app is ready."""
        # Add defaults to Django settings.py if not already set in user project
        self.apply_default_settings()

        # Re-configure logging for the MCP app
        configure_logging()

        # Apply logging patch if configured
        if settings.MCP_PATCH_SDK_TOOL_LOGGING:
            logger.debug("Applying MCP SDK tool logging patch")
            patch_mcp_tool_decorator(mcp_app)

        # Apply context patch if configured
        if settings.MCP_PATCH_SDK_GET_CONTEXT:
            logger.debug("Applying MCP SDK get_context patch for URL params")
            patch_mcp_get_context(mcp_app)

        # Load MCP modules from Django apps
        register_mcp_modules()
        tools = mcp_app._tool_manager.list_tools()

        # Log registered MCP tools if configured
        if settings.MCP_LOG_TOOL_REGISTRATION:
            log_descriptions = settings.MCP_LOG_TOOL_DESCRIPTIONS
            for tool in tools:
                description = f" - {tool.description}" if log_descriptions else ""
                logger.info(f"Registered MCP tool: {tool.name}{description}")
