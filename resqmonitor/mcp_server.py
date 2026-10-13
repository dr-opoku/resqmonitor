"""Optional, read-only MCP tools over supplied text and synthetic resources."""

from __future__ import annotations

from typing import Any, Literal

from .demo import demo
from .engine import analyze


def serve() -> None:
    try:
        from mcp.server import MCPServer
        from mcp.types import ToolAnnotations
    except ImportError as exc:
        raise ImportError("MCP support requires: python -m pip install '.[mcp]'") from exc

    server = MCPServer("resqmonitor")
    annotations = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False)

    @server.tool(annotations=annotations)
    def inspect_results(csv_text: str, config: dict[str, Any] | None = None,
                        baseline_csv: str | None = None) -> dict[str, Any]:
        """Compare supplied predictions and outcomes. Does not read files, call models, or generate outcome labels."""
        return analyze(csv_text, config, baseline_csv=baseline_csv)

    @server.tool(annotations=annotations)
    def demonstrate_result_quality(scenario: Literal["healthy", "degraded", "unknown"] = "degraded") -> dict[str, Any]:
        """Return a report over bundled synthetic classification results and baseline."""
        return demo(scenario)

    server.run(transport="stdio")
