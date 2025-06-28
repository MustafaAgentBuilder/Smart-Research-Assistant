from agents import RunHooks, RunContextWrapper
from typing import Any

class MyRunHooks(RunHooks):
    def __init__(self):
        # Dictionary to count how many times each hook is triggered
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
        print(f"### {self.name}: Run ended with output: {output}. Count: {self.event_counts['on_run_end']}. Usage: {context.usage}")

    async def on_run_exception(self, context: RunContextWrapper, exception: Exception) -> None:
        self.event_counts['on_run_exception'] += 1
        print(f"### {self.name}: Run exception: {exception}. Count: {self.event_counts['on_run_exception']}. Usage: {context.usage}")