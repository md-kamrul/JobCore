from __future__ import annotations

import asyncio
import json
import pathlib
import sys

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def _tool_result_json(result):
	"""Best-effort decode of a Python MCP tool result into a dict."""
	if not hasattr(result, "content") or not result.content:
		return None
	first = result.content[0]

	data = getattr(first, "json", None)
	if isinstance(data, dict):
		return data

	text = getattr(first, "text", None)
	if isinstance(text, str):
		try:
			parsed = json.loads(text)
			return parsed if isinstance(parsed, dict) else None
		except Exception:
			return None

	return None


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

			start = await session.call_tool(
				"start_google_form_session",
				{
					"url": form_url,
					"timeout_seconds": 30,
					"visible_browser": True,
					"pause_seconds": 5,
					"max_questions": 50,
				},
			)

			# Task 3 complete: session started and questions read
			await asyncio.sleep(5)

			data = _tool_result_json(start)

			if not isinstance(data, dict):
				# Fallback: print raw tool output
				if hasattr(start, "content") and start.content:
					first = start.content[0]
					print(getattr(first, "text", None) or str(first))
				else:
					print(str(start))
				print("Could not parse questions from MCP response.")
				return

			session_id = data.get("session_id")
			questions = data.get("questions", [])
			if not session_id or not isinstance(questions, list) or not questions:
				print("No questions found or invalid session.")
				return

			for q in questions:
				qnum = q.get("number")
				qtext = q.get("text")
				qtype = q.get("type")
				opts = q.get("options") or []
				print(f"\nQ{qnum} ({qtype}): {qtext}")
				if opts:
					for i, opt in enumerate(opts, start=1):
						print(f"  {i}. {opt}")

				while True:
					answer = input("Answer (press Enter to continue): ")
					await asyncio.sleep(5)

					try:
						resp = await session.call_tool(
							"answer_google_form_question",
							{
								"session_id": session_id,
								"question_number": int(qnum),
								"answer": answer,
								"timeout_seconds": 30,
								"pause_seconds": 5,
							},
						)
						break
					except Exception as e:
						print(f"Error answering Q{qnum}: {e}")
						print("Try again.")

				# Task 4 complete: one question answered
				await asyncio.sleep(5)

				if hasattr(resp, "content") and resp.content:
					first = resp.content[0]
					text = getattr(first, "text", None)
					print(text if text is not None else str(first))
				else:
					print(str(resp))

				# Task 5 complete: status printed
				await asyncio.sleep(5)

			sub = await session.call_tool(
				"submit_google_form_session",
				{
					"session_id": session_id,
					"timeout_seconds": 30,
					"keep_browser_open_seconds": 2,
					"pause_seconds": 5,
				},
			)

			# Task 6 complete: form submitted
			await asyncio.sleep(5)

			if hasattr(sub, "content") and sub.content:
				first = sub.content[0]
				text = getattr(first, "text", None)
				print(text if text is not None else str(first))
			else:
				print(str(sub))

			# Task 7 complete: submit result printed
			await asyncio.sleep(5)

			await session.call_tool(
				"close_google_form_session",
				{"session_id": session_id, "pause_seconds": 0},
			)

			# Task 8 complete: session closed
			await asyncio.sleep(5)


if __name__ == "__main__":
	asyncio.run(run_agent())
