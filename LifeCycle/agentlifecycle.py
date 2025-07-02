from agents import AgentHooks, RunContextWrapper, Agent ,TContext
from typing import Any
  # import your context class

class MyAgentHooks(AgentHooks[TContext]):
    def __init__(self):
        self.event_counts = {k: 0 for k in [
            'on_agent_start', 'on_agent_end', 'on_agent_exception',
            'on_handoff', 'on_tool_start', 'on_tool_end',
            'on_message', 'on_thought', 'on_action',
        ]}
        self.name = "MyAgentHooks"

    async def on_start(self, context: RunContextWrapper[TContext], agent: Agent[TContext]) -> None:
        self.event_counts['on_agent_start'] += 1
        print(f"### {self.name}: Agent {agent.name} started"
              f" Count: {self.event_counts['on_agent_start']}. Usage: {context.usage}")

    async def on_end(self, context: RunContextWrapper[TContext], agent: Agent[TContext], output: Any) -> None:
        self.event_counts['on_agent_end'] += 1
        print(f"### {self.name}: Agent {agent.name} ended with output: {output}"
              f" Count: {self.event_counts['on_agent_end']}. Usage: {context.usage}")

    async def on_agent_exception(self, context: RunContextWrapper[TContext], agent: Agent[TContext], exception: Exception) -> None:
        self.event_counts['on_agent_exception'] += 1
        print(f"### {self.name}: Agent {agent.name} exception: {exception} "
              f"Count: {self.event_counts['on_agent_exception']}. Usage: {context.usage}")

    async def on_handoff(self, context: RunContextWrapper[TContext], agent: Agent[TContext], source: Agent[TContext]) -> None:
        self.event_counts['on_handoff'] += 1
        print(f"### {self.name}: Handoff to agent {agent.name} from {source.name}"
              f" Count: {self.event_counts['on_handoff']}")

    async def on_tool_start(self, context: RunContextWrapper[TContext], agent: Agent[TContext], tool: Any) -> None:
        self.event_counts['on_tool_start'] += 1
        print(f"### {self.name}: Tool {tool.name} started by {agent.name}"
              f" Count: {self.event_counts['on_tool_start']}")

    async def on_tool_end(self, context: RunContextWrapper[TContext], agent: Agent[TContext], tool: Any, result: Any) -> None:
        self.event_counts['on_tool_end'] += 1
        print(f"### {self.name}: Tool {tool.name} ended with result: {result}"
              f" Count: {self.event_counts['on_tool_end']}")

    async def on_message(self, context: RunContextWrapper[TContext], agent: Agent[TContext], message_event: Any, **kwargs) -> None:
        self.event_counts['on_message'] += 1
        content = getattr(message_event, 'content', 'unknown')
        print(f"### {self.name}: Message: {content}"
              f" Count: {self.event_counts['on_message']}")

    async def on_thought(self, context: RunContextWrapper[TContext], agent: Agent[TContext], thought_event: Any, **kwargs) -> None:
        self.event_counts['on_thought'] += 1
        content = getattr(thought_event, 'content', 'unknown')
        print(f"### {self.name}: Thought: {content}"
              f" Count: {self.event_counts['on_thought']}")

    async def on_action(self, context: RunContextWrapper[TContext ], agent: Agent[TContext], action_event: Any, **kwargs) -> None:
        self.event_counts['on_action'] += 1
        action = getattr(action_event, 'action', 'unknown')
        print(f"### {self.name}: Action: {action}"
              f" Count: {self.event_counts['on_action']}")
