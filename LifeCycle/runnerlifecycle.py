from agents import RunHooks, RunContextWrapper
from typing import Any

class MyRunHooks(RunHooks):
    def __init__(self):
        self.event_counts = {
            'on_run_start': 0,
            'on_run_end': 0,
            'on_run_exception': 0,
        }
        self.name = "MyRunHooks"

    async def on_run_start(self, context: RunContextWrapper) -> None:
        self.event_counts['on_run_start'] += 1
        print(f"### {self.name}: Run started. Count: {self.event_counts['on_run_start']}. Usage: {context.usage}")

    async def on_run_end(self, context: RunContextWrapper, output: Any) -> None:
        self.event_counts['on_run_end'] += 1
        print("--- Agent run finished ---")
        print(f"Final result: {output}")
        # Extract and format RunResult details
        if hasattr(output, 'last_agent'):
            print(f"- Last agent: {output.last_agent}")
        if hasattr(output, 'final_output'):
            print(f"- Final output (str):\n    {output.final_output}")
        if hasattr(output, 'new_items'):
            print(f"- {len(output.new_items)} new item(s)")
        if hasattr(output, 'raw_responses'):
            print(f"- {len(output.raw_responses)} raw response(s)")
        if hasattr(output, 'input_guardrail_results'):
            print(f"- {len(output.input_guardrail_results)} input guardrail result(s)")
        if hasattr(output, 'output_guardrail_results'):
            print(f"- {len(output.output_guardrail_results)} output guardrail result(s)")
        print("(See `RunResult` for more details)")

    async def on_run_exception(self, context: RunContextWrapper, exception: Exception) -> None:
        self.event_counts['on_run_exception'] += 1
        print(f"### {self.name}: Run exception: {exception}. Count: {self.event_counts['on_run_exception']}. Usage: {context.usage}")

    # async def on_handoff(self, context: RunContextWrapper, handoff_event: Any, **kwargs) -> None:
    #     self.event_counts['on_handoff'] += 1
    #     print(f"### {self.name}: Handoff event: {handoff_event}. Count: {self.event_counts['on_handoff']}")

    async def on_tool_call(self, context: RunContextWrapper, tool_call_event: Any, **kwargs) -> None:
        self.event_counts['on_tool_call'] += 1
        print(f"### {self.name}: Tool call event: {tool_call_event}. Count: {self.event_counts['on_tool_call']}")

    async def on_tool_result(self, context: RunContextWrapper, tool_result_event: Any, **kwargs) -> None:
        self.event_counts['on_tool_result'] += 1
        print(f"### {self.name}: Tool result event: {tool_result_event}. Count: {self.event_counts['on_tool_result']}")

    async def on_message(self, context: RunContextWrapper, message_event: Any, **kwargs) -> None:
        self.event_counts['on_message'] += 1
        print(f"### {self.name}: Message event: {message_event}. Count: {self.event_counts['on_message']}")

    async def on_thought(self, context: RunContextWrapper, thought_event: Any, **kwargs) -> None:
        self.event_counts['on_thought'] += 1
        print(f"### {self.name}: Thought event: {thought_event}. Count: {self.event_counts['on_thought']}")

    async def on_action(self, context: RunContextWrapper, action_event: Any, **kwargs) -> None:
        self.event_counts['on_action'] += 1
        print(f"### {self.name}: Action event: {action_event}. Count: {self.event_counts['on_action']}")