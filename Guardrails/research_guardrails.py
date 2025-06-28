import os
from pydantic import BaseModel, Field
from typing import Union, List
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    input_guardrail,
    output_guardrail,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    OpenAIChatCompletionsModel,
)

Provider = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash-exp",
    openai_client=Provider,
)

# 2️⃣ Research_Agent INPUT guardrail
# ======================================================

class ResearchInputGuard(BaseModel):
    is_valid_question: bool = Field(False, description="True if input is a clear research request")
    reasoning: str         = Field("", description="Why input was accepted or not")

research_input_judge = Agent(
    name="Research_Input_Guardrail",
    model=model,
    instructions="""
Check if the user input is a clear, specific research query (e.g. 'Find info about X', 'Tell me the latest on Y'). 
Reject greetings or vague inputs like 'Hi', 'Tell me something'.
Return JSON matching the ResearchInputGuard schema.
""",
    output_type=ResearchInputGuard,
)

@input_guardrail
async def research_input_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    user_input: Union[str, List]
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        research_input_judge,
        user_input,
        context=ctx.context
    )
    print(f"### Research Input Guardrail: ")
    verdict: ResearchInputGuard = result.final_output
    trip = not verdict.is_valid_question
    return GuardrailFunctionOutput(output_info=verdict, tripwire_triggered=trip)

# ======================================================
# 3️⃣ Research_Agent OUTPUT guardrail
# ======================================================

class ResearchOutputGuard(BaseModel):
    has_content: bool         = Field(False, description="True if output includes research content")
    no_tool_mentions: bool    = Field(False, description="True if output has no raw tool or system language")
    reasoning: str            = Field("", description="Why output passed or failed")

research_output_judge = Agent(
    name="Research_Output_Guardrail",
    model=model,
    instructions="""
You receive the Research Agent’s raw output. 
Check that:
  1) It contains factual research content.
  2) It does NOT mention tool names or system-level instructions (like 'I used Tavily').
Return JSON matching the ResearchOutputGuard schema.
""",
    output_type=ResearchOutputGuard,
)

@output_guardrail
async def research_output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        research_output_judge,
        output,
        context=ctx.context
    )
    print(f"### Research Output Guardrail: ")
    verdict: ResearchOutputGuard = result.final_output
    if not (verdict.has_content and verdict.no_tool_mentions):
        raise OutputGuardrailTripwireTriggered(verdict.reasoning)
    
    return GuardrailFunctionOutput(output_info=verdict, tripwire_triggered=verdict.has_content is False or verdict.no_tool_mentions is False)