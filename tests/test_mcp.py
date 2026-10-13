"""Optional SDK contract and real local-stdio round-trip checks."""

import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from resqmonitor.demo import SCENARIOS, demo

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec("mcp"), "Install .[mcp] to check the optional adapter")
class MCPTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from resqmonitor.mcp_server import create_server
        self.server = create_server()

    async def test_advertised_schema_matches_documented_contract(self):
        documented = json.loads((ROOT / "docs/report.schema.json").read_text())
        documented.pop("$schema")
        tools = await self.server.list_tools()
        self.assertEqual({tool.name for tool in tools}, {"inspect_results", "demonstrate_result_quality"})
        for tool in tools:
            self.assertEqual(tool.output_schema, documented)
            self.assertTrue(tool.annotations.read_only_hint)

    async def test_every_demo_has_valid_structured_output(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                result = await self.server.call_tool("demonstrate_result_quality", {"scenario": scenario})
                self.assertFalse(result.is_error)
                self.assertEqual(result.structured_content, demo(scenario))

    async def test_inspect_preserves_unknown_and_fixed_time(self):
        result = await self.server.call_tool("inspect_results", {"csv_text": "record_id,predicted_label,actual_label\n", "at": "2026-10-13T12:00:00Z"})
        self.assertFalse(result.is_error)
        self.assertEqual(result.structured_content["status"], "unknown")
        self.assertFalse(result.structured_content["synthetic"])
        self.assertEqual(result.structured_content["evaluated_at"], "2026-10-13T12:00:00+00:00")

    async def test_stdio_discovery_unknown_and_input_error(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        params = StdioServerParameters(command=sys.executable, args=["-m", "resqmonitor", "serve"], cwd=ROOT)
        async with asyncio.timeout(20):
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    self.assertTrue(all(tool.output_schema for tool in tools.tools))
                    normal = await session.call_tool("demonstrate_result_quality", {"scenario": "small_sample"})
                    self.assertFalse(normal.is_error)
                    self.assertEqual(normal.structured_content["status"], "unknown")
                    invalid = await session.call_tool("inspect_results", {"csv_text": "id,id\na,b\n"})
                    self.assertTrue(invalid.is_error)
                    self.assertIsNone(invalid.structured_content)
                    self.assertIn("unique", invalid.content[0].text)
