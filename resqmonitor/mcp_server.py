"""Optional, read-only MCP tools over supplied text and synthetic resources."""

from __future__ import annotations

from typing import Any, Literal

try:
    from ._mcp_contract import Report
except ImportError as exc:
    raise ImportError("MCP support requires: python -m pip install '.[mcp]'") from exc

from .demo import demo
from .engine import analyze


def create_server() -> Any:
    try:
        from mcp.server import MCPServer
        from mcp.server.mcpserver.exceptions import ToolError
        from mcp.types import ToolAnnotations
    except ImportError as exc:
        raise ImportError("MCP support requires: python -m pip install '.[mcp]'") from exc

    server = MCPServer("resqmonitor")
    annotations = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False)

    @server.tool(annotations=annotations, structured_output=True)
    def inspect_results(csv_text: str, config: dict[str, Any] | None = None,
                        baseline_csv: str | None = None, at: str | None = None) -> Report:
        """Compare supplied predictions and outcomes. Does not read files, call models, or generate outcome labels."""
        try:
            return analyze(csv_text, config, baseline_csv=baseline_csv, at=at)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc

    @server.tool(annotations=annotations, structured_output=True)
    def demonstrate_result_quality(scenario: Literal["healthy", "degraded", "unknown", "small_sample"] = "degraded") -> Report:
        """Return a report over bundled synthetic classification results and baseline."""
        return demo(scenario)

    return server


def serve() -> None:
    create_server().run(transport="stdio")
