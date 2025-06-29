from agents import AgentHooks, RunContextWrapper, Agent
from typing import Any

class MyAgentHooks(AgentHooks):
    def __init__(self):
        self.event_counts = {
            'on_agent_start': 0,
            'on_agent_end': 0,
            'on_agent_exception': 0,
            'on_handoff': 0,
            'on_tool_call': 0,
            'on_tool_result': 0,
            'on_message': 0,
            'on_thought': 0,
            'on_action': 0,
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

    # async def on_handoff(self, agent: Agent, context: RunContextWrapper, handoff_event: Any, from_agent: Agent = None, **kwargs) -> None:
    #     self.event_counts['on_handoff'] += 1
    #     target_name = getattr(handoff_event, 'target_agent', None).name if hasattr(handoff_event, 'target_agent') else 'unknown'
    #     from_name = from_agent.name if from_agent else 'unknown'
    #     print(f"### {self.name}: Handoff from agent {from_name} to {target_name}. Count: {self.event_counts['on_handoff']}")

    async def on_tool_call(self, agent: Agent, context: RunContextWrapper, tool_call_event: Any, **kwargs) -> None:
        self.event_counts['on_tool_call'] += 1
        tool_name = getattr(tool_call_event, 'tool_name', 'unknown')
        print(f"### {self.name}: Tool call by agent {agent.name}: {tool_name}. Count: {self.event_counts['on_tool_call']}")

    async def on_tool_result(self, agent: Agent, context: RunContextWrapper, tool_result_event: Any, **kwargs) -> None:
        self.event_counts['on_tool_result'] += 1
        result = getattr(tool_result_event, 'result', 'unknown')
        print(f"### {self.name}: Tool result for agent {agent.name}: {result}. Count: {self.event_counts['on_tool_result']}")

    async def on_message(self, agent: Agent, context: RunContextWrapper, message_event: Any, **kwargs) -> None:
        self.event_counts['on_message'] += 1
        content = getattr(message_event, 'content', 'unknown')
        print(f"### {self.name}: Message from agent {agent.name}: {content}. Count: {self.event_counts['on_message']}")

    async def on_thought(self, agent: Agent, context: RunContextWrapper, thought_event: Any, **kwargs) -> None:
        self.event_counts['on_thought'] += 1
        content = getattr(thought_event, 'content', 'unknown')
        print(f"### {self.name}: Thought from agent {agent.name}: {content}. Count: {self.event_counts['on_thought']}")

    async def on_action(self, agent: Agent, context: RunContextWrapper, action_event: Any, **kwargs) -> None:
        self.event_counts['on_action'] += 1
        action = getattr(action_event, 'action', 'unknown')
        print(f"### {self.name}: Action by agent {agent.name}: {action}. Count: {self.event_counts['on_action']}")