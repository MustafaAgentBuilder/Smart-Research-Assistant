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

class SummaryInputGuard(BaseModel):
    is_valid_text: bool = Field(False, description="True if input is a text block to summarize")
    reasoning: str      = Field("", description="Why input was accepted or not")

summary_input_judge = Agent(
    name="Summary_Input_Guardrail",
    model=model,
    instructions="""
Check if the input is a non-empty text block or factual content to summarize.
Reject questions, greetings, or very short text (<20 characters).
Return JSON matching the SummaryInputGuard schema.
""",
    output_type=SummaryInputGuard,
)

@input_guardrail
async def summary_input_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    user_input: Union[str, List]
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        summary_input_judge,
        user_input,
        context=ctx.context
    )
    print(f"### Summary Input Guardrail: ")
    verdict: SummaryInputGuard = result.final_output
    trip = not verdict.is_valid_text
    return GuardrailFunctionOutput(output_info=verdict, tripwire_triggered=trip)




# —————————————————————————————————————
#  2️⃣ Output Guardrail Schema & Agent
# —————————————————————————————————————
class SummaryOutputGuardrail(BaseModel):
    out_of_context: bool = Field(False, description="True if output is off-topic or irrelevant")
    contains_prohibited: bool = Field(False, description="True if output contains disallowed content")
    reasoning: str = Field("", description="Why the output was flagged or allowed")

guardrail_judge = Agent(
    name="Summary_Output_Guardrail",
    model=model,
    instructions=(
        "You are a guardrail reviewing the Summary Agent’s output. "
        "Detect if it’s out-of-context or contains disallowed content. "
        "Return JSON matching SummaryOutputGuardrail schema."
    ),
    output_type=SummaryOutputGuardrail,
)

@output_guardrail
async def summary_output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: SummaryOutputGuardrail  # or str, but here we adapt to your flow
) -> GuardrailFunctionOutput:
    """
    Output guardrail that flags off-topic or prohibited summary content.
    """
    # If output is a Pydantic model, get its text field; else assume str
    text = getattr(output, "response", output)

    result = await Runner.run(
        guardrail_judge,
        text,
        context=ctx.context
    )
    print(f"### Summary Output Guardrail: ")
    verdict: SummaryOutputGuardrail = result.final_output
    trip = verdict.out_of_context or verdict.contains_prohibited

    return GuardrailFunctionOutput(
        output_info=verdict,
        tripwire_triggered=trip
    )
