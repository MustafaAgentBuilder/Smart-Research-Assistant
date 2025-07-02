# agents.py
import os, asyncio
from pathlib import Path
import agentops
import aiofiles
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents.extensions import handoff_filters
from Guardrails.Triage_guardrails import triage_agent_guardrail, triage_output_guardrail
from Guardrails.research_guardrails import research_input_guardrail, research_output_guardrail
from Guardrails.summary_guardrail import summary_input_guardrail, summary_output_guardrail
from Context.dynamic import dynamic_context_wrapper, LocalContext
from Tool.search_tool import search_web
from LifeCycle.runnerlifecycle import MyRunHooks
from LifeCycle.agentlifecycle import MyAgentHooks
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    handoff,
    set_tracing_disabled,
    ItemHelpers,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered
)

load_dotenv()
set_tracing_disabled(True)


from agents import enable_verbose_stdout_logging

# enable_verbose_stdout_logging()
# Setup provider & model
Provider = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash-lite-preview-06-17",
    openai_client=Provider,
)

# agentops.init('Add Your AgentOps API Key here') 
# Summary Agent
summary_Agent = Agent(
    name="Summary_Agent",
    model=model,
    instructions="""
You are the Summary Agent. You receive raw search results (list of {title, url, summary}).
1. Step 1: Review each result briefly.
2. Step 2: Extract the three most important insights.
3. Step 3: Summarize them in 3 concise bullet points.
4. Step 4: Provide a final “Sources:” section listing URLs.
5. Step 5: Return the summary in Markdown format.

Be concise, factual, and omit any irrelevant info.
""", 
    output_guardrails=[summary_output_guardrail],
    input_guardrails=[summary_input_guardrail],
)

# Research Agent
research_Agent = Agent(
    name="Research_Agent",
    model=model,
    tools=[search_web],
    input_guardrails=[research_input_guardrail],
    output_guardrails=[research_output_guardrail],
    handoffs=[
        handoff(
            agent=summary_Agent,
            tool_name_override="to_summary",
            tool_description_override="Pass raw search results to Summary_Agent.",
            input_filter=handoff_filters.remove_all_tools,
        )
    ],
    instructions="""
You are the Research Agent. Your goal is to gather raw data on the user’s topic.
1. StepEn Step 1: Analyze the user’s request to form a precise search query.
2. Step 2: CALL_TOOL search_web with that query.
3. Step 3: Collect the results (title, url, summary) in JSON form.
4. Step 4: Think about whether the results cover the topic.
5. Finally, emit HANDOFF: to_summary, attaching the raw results.

Make your reasoning clear and only then hand off to Summary_Agent.
"""
)

hooks=MyAgentHooks()
hooks.on_start
hooks.on_end
hooks.on_action
hooks.on_agent_exception
hooks.on_tool_start
hooks.on_tool_end
hooks.on_thought
hooks.on_message
hooks.on_handoff




# Triage Agent
Triage_Agent = Agent[LocalContext](
    name="Triage_Agent",
    model=model,
    instructions=dynamic_context_wrapper,
    handoffs=[
        handoff(
            agent=research_Agent,
            tool_name_override="go_research",
            tool_description_override="Fetch fresh research with Research_Agent.",
        ),
    ],
    input_guardrails=[triage_agent_guardrail],
    output_guardrails=[triage_output_guardrail],
    hooks=hooks,
)

# Main async loop
async def save_context(context, file_path):
    async with aiofiles.open(file_path, "w") as f:
        await f.write(json.dumps(context.model_dump(), indent=2))

async def project():
    while True:
        user_id = input("Enter your user ID: ")
        user_name = input("Enter your name: ")
        context_file = Path(f"context_{user_id}.json")

        if context_file.exists():
            print("❗ A conversation file with this ID or name already exists. Please use a different one.")
        else:
            break

    context = LocalContext(
        user_id=user_id,
        name=user_name,
        query="",
        has_data_to_summarize=False,
        source_type="text",
        search_needed=True,
        preferred_language="en",
        history=[],
    )
    print(f"Created new context for user {user_id}")
    await save_context(context, context_file)

    # runner_lifecycle = MyRunHooks()
    # runner = Runner(hooks=runner_lifecycle)  # Instantiate Runner with hooks

    while True:
        q = input("Enter topic or 'exit': ")
        if q.lower() == "exit":
            break

        # print("=== Run starting ===")

        try:
            context.name = user_name
            context.query = q
            context.has_data_to_summarize = False
            context.source_type = "text"
            context.search_needed = True
            context.preferred_language = "en"
            context.history.append({"role": "user", "content": q})
            await save_context(context, context_file)

            run_hook = MyRunHooks()
            run_hook.on_run_start
            run_hook.on_run_end



            response = Runner.run_streamed(
                starting_agent=Triage_Agent,
                input=q,
                context=context,
                hooks=run_hook,  # Pass hooks to Runner
            )

            async for event in response.stream_events():
                if event.type == "raw_response_event":
                    continue
                elif event.type == "agent_updated_stream_event":
                    print(f"Agent updated: {event.new_agent.name}")
                elif event.type == "run_item_stream_event":
                    if event.item.type == "tool_call_item":
                        print("-- Tool was called")
                    elif event.item.type == "tool_call_output_item":
                        print(f"-- Tool output: {event.item.output}")
                    elif event.item.type == "message_output_item":
                        message = ItemHelpers.text_message_output(event.item)
                        print(f"-- Message output:\n {message}")
                        context.history.append({"role": "assistant", "content": message})
                        await save_context(context, context_file)
                else:
                    pass

        except InputGuardrailTripwireTriggered:
            print("Input flagged by guardrail. Please rephrase your request.\n")
        except OutputGuardrailTripwireTriggered:
            print("Output flagged by guardrail. Please try again later.\n")
        except KeyError as ke:
            print(f"Missing field in event: {ke}\n")
        except Exception as e:
            print(f"Error during run: {e}\n")

        # print("=== Run complete ===\n")

if __name__ == "__main__":
    asyncio.run(project())