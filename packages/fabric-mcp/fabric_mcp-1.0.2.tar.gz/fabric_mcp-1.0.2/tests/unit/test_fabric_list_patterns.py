"""Unit tests for fabric_list_patterns MCP tool."""

import inspect

import pytest
from fastmcp.tools import Tool
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR

from tests.shared.fabric_api.base import TestFixturesBase
from tests.shared.fabric_api_mocks import (
    FabricApiMockBuilder,
    assert_api_client_calls,
    assert_unexpected_error_test,
    mock_fabric_api_client,
)


class TestFabricListPatterns(TestFixturesBase):
    """Test cases for the fabric_list_patterns MCP tool."""

    def test_successful_response_with_multiple_patterns(
        self, mcp_tools: dict[str, Tool]
    ):
        """Test successful API response with multiple pattern names."""
        # Arrange
        patterns = ["summarize", "explain", "improve_writing"]
        builder = FabricApiMockBuilder().with_successful_pattern_list(patterns)

        fabric_list_patterns = getattr(mcp_tools["fabric_list_patterns"], "fn")

        # Act
        with mock_fabric_api_client(builder) as mock_client:
            result = fabric_list_patterns()

        # Assert
        assert result == patterns
        assert_api_client_calls(mock_client, "/patterns/names")

    def test_successful_response_with_empty_list(self, mcp_tools: dict[str, Tool]):
        """Test successful API response with empty pattern list."""
        # Arrange
        builder = FabricApiMockBuilder().with_successful_pattern_list([])

        fabric_list_patterns = getattr(mcp_tools["fabric_list_patterns"], "fn")

        # Act
        with mock_fabric_api_client(builder) as mock_client:
            result = fabric_list_patterns()

        # Assert
        assert result == []
        assert_api_client_calls(mock_client, "/patterns/names")

    def test_connection_error_handling(self, mcp_tools: dict[str, Tool]):
        """Test handling of connection errors (httpx.RequestError)."""
        # Arrange
        builder = FabricApiMockBuilder().with_connection_error(
            "Failed to connect to Fabric API"
        )

        fabric_list_patterns = getattr(mcp_tools["fabric_list_patterns"], "fn")

        # Act & Assert
        with mock_fabric_api_client(builder) as _:
            with pytest.raises(McpError) as exc_info:
                fabric_list_patterns()

            assert "Failed to connect to Fabric API" in str(
                exc_info.value.error.message
            )
            assert exc_info.value.error.code == INTERNAL_ERROR

    def test_http_status_error_handling(self, mcp_tools: dict[str, Tool]):
        """Test handling of HTTP status errors (httpx.HTTPStatusError)."""
        # Arrange
        builder = FabricApiMockBuilder().with_http_error(
            status_code=500, response_text="Internal Server Error"
        )

        fabric_list_patterns = getattr(mcp_tools["fabric_list_patterns"], "fn")

        # Act & Assert
        with mock_fabric_api_client(builder) as mock_client:
            with pytest.raises(McpError) as exc_info:
                fabric_list_patterns()

            assert (
                "Fabric API error during retrieving patterns: 500 Internal Server Error"
                in str(exc_info.value.error.message)
            )
            assert exc_info.value.error.code == INTERNAL_ERROR
            assert_api_client_calls(mock_client, "/patterns/names")

    def test_json_parsing_error_handling(self, mcp_tools: dict[str, Tool]):
        """Test handling of JSON parsing errors."""
        # Arrange
        builder = FabricApiMockBuilder().with_json_decode_error("Invalid JSON")

        fabric_list_patterns = getattr(mcp_tools["fabric_list_patterns"], "fn")

        # Act & Assert
        with mock_fabric_api_client(builder) as mock_client:
            with pytest.raises(McpError) as exc_info:
                fabric_list_patterns()

        assert "Unexpected error during retrieving patterns" in str(
            exc_info.value.error.message
        )
        assert exc_info.value.error.code == INTERNAL_ERROR
        assert_api_client_calls(mock_client, "/patterns/names")

    def test_unexpected_exception_handling(self, mcp_tools: dict[str, Tool]):
        """Test handling of unexpected exceptions."""
        fabric_list_patterns = getattr(mcp_tools["fabric_list_patterns"], "fn")
        assert_unexpected_error_test(
            fabric_list_patterns,
            "Unexpected error during retrieving patterns",
        )

    def test_tool_signature_and_return_type(self, mcp_tools: dict[str, Tool]):
        """Test that the tool has the correct signature and return type annotation."""
        fabric_list_patterns = getattr(mcp_tools["fabric_list_patterns"], "fn")
        # Get the function signature
        sig = inspect.signature(fabric_list_patterns)

        # Verify no parameters
        assert len(sig.parameters) == 0

        # Verify return type annotation
        assert sig.return_annotation == list[str]

    def test_tool_docstring(self, mcp_tools: dict[str, Tool]):
        """Test that the tool has appropriate documentation."""
        fabric_list_patterns = getattr(mcp_tools["fabric_list_patterns"], "fn")
        assert fabric_list_patterns.__doc__ is not None
        assert "available fabric patterns" in fabric_list_patterns.__doc__.lower()
