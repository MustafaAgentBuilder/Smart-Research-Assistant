from agents import AgentHooks, RunContextWrapper, Agent
from typing import Any

class MyAgentHooks(AgentHooks):
    def __init__(self):
        # Dictionary to count how many times each hook is triggered
        self.event_counts = {
            'on_agent_start': 0,
            'on_agent_end': 0,
            'on_agent_exception': 0,
        }
        self.name = "MyAgentHooks"

    async def on_agent_start(self, agent: Agent, context: RunContextWrapper) -> None:
        self.event_counts['on_agent_start'] += 1
        print(f"### {self.name}: Agent {agent.name} started. Count: {self.event_counts['on_agent_start']}. Usage: {context.usage}")

    async def on_agent_end(self, agent: Agent, context: RunContextWrapper, output: Any) -> None:
        self.event_counts['on_agent_end'] += 1
        print(f"### {self.name}: Agent {agent.name} ended with output: {output}. Count: {self.event_counts['on_agent_end']}. Usage: {context.usage}")

    async def on_agent_exception(self, agent: Agent, context: RunContextWrapper, exception: Exception) -> None:
        self.event_counts['on_agent_exception'] += 1
        print(f"### {self.name}: Agent {agent.name} exception: {exception}. Count: {self.event_counts['on_agent_exception']}. Usage: {context.usage}")

# Usage example:
# from openai_agents import Agent, Runner
# agent_hooks = MyAgentHooks()
# agent = Agent(name="TestAgent", hooks=agent_hooks, ...)
# runner = Runner()
# runner.run(agent, input_data, context)
#
# To save logs to a file instead of printing, you could modify like this:
# import logging
# logging.basicConfig(filename='agent_hooks.log', level=logging.INFO)
# Replace print() with logging.info() in each method.