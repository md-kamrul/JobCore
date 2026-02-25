from __future__ import annotations

import asyncio
import pathlib
import sys

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def run_agent() -> None:
	form_url = input("Enter Google Form URL: ").strip()
	if not form_url:
		print("No URL provided. Exiting.")
		return

	# Task 1 complete: got URL
	await asyncio.sleep(5)

	server_path = str(pathlib.Path(__file__).with_name("mcp_form_server.py").resolve())
	server_params = StdioServerParameters(
		command=sys.executable,
		args=[server_path],
	)

	async with stdio_client(server_params) as (read_stream, write_stream):
		async with ClientSession(read_stream, write_stream) as session:
			await session.initialize()

			# Task 2 complete: MCP session initialized
			await asyncio.sleep(5)

			result = await session.call_tool(
				"submit_google_form",
				{
					"url": form_url,
					"timeout_seconds": 30,
					"visible_browser": True,
					"keep_browser_open_seconds": 2,
					"pause_seconds": 5,
				},
			)

			# Task 3 complete: form automation executed
			await asyncio.sleep(5)

			# MCP tool results are typically returned as a list of content blocks.
			# We print a best-effort readable representation.
			if hasattr(result, "content") and result.content:
				first = result.content[0]
				text = getattr(first, "text", None)
				print(text if text is not None else str(first))
			else:
				print(str(result))

			# Task 4 complete: output printed
			await asyncio.sleep(2)


if __name__ == "__main__":
	asyncio.run(run_agent())
