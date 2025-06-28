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
# from tavily import TavilyClient  # if you still need it for search_web

# —————————————————————————————————————
#  Provider & model setup (unchanged)
# —————————————————————————————————————
Provider = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash-exp",
    openai_client=Provider,
)

# —————————————————————————————————————
#  1️⃣ Input Guardrail Schema & Agent
# —————————————————————————————————————
class TriageAgentGuardrail(BaseModel):
    is_abusive: bool = Field(False, description="True if input is abusive or harmful")
    is_offensive: bool = Field(False, description="True if input is offensive or inappropriate")
    reasoning: str = Field("", description="Why the input was flagged or allowed")

guardrail_agent = Agent(
    name="Triage_Agent_Guardrail",
    model=model,
    instructions=(
        "You are a guardrail checking user input for abuse/offense. "
        "Return JSON matching the TriageAgentGuardrail schema."
    ),
    output_type=TriageAgentGuardrail,
)

@input_guardrail
async def triage_agent_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    user_input: Union[str, List]
) -> GuardrailFunctionOutput:
    """
    Input guardrail that flags abusive or offensive user input.
    """
    # Run the small guardrail agent with same context
    result = await Runner.run(
        guardrail_agent,
        user_input,
        context=ctx.context
    )
    verdict: TriageAgentGuardrail = result.final_output
    trip = verdict.is_abusive or verdict.is_offensive
    print(f"### Triage Agent Input Guardrail: {verdict}")
    return GuardrailFunctionOutput(
        output_info=verdict,
        tripwire_triggered=trip
    )



# ======================================================
# 1️⃣ Triage_Agent OUTPUT guardrail
# ======================================================
# Your existing Pydantic schema
class TriageOutputGuard(BaseModel):
    valid_handoff: bool = Field(False, description="True if HANDOFF is go_research or go_summary")
    reasoning: str    = Field("", description="Why the handoff was accepted or rejected")

# Your existing handoff_judge agent
# handoff_judge = Agent(...)

@output_guardrail
async def triage_output_guardrail(
    ctx: RunContextWrapper,
    agent,       # Agent – unused here
    output: str  # The raw text the Triage_Agent produced
) -> GuardrailFunctionOutput:
    # 1️⃣ If it's not a HANDOFF token, let it pass
    if not output.strip().upper().startswith("HANDOFF:"):
        return GuardrailFunctionOutput(
            output_info=TriageOutputGuard(
                valid_handoff=True,
                reasoning="Non-handoff message – allowed."
            ),
            tripwire_triggered=False
        )

    # 2️⃣ Otherwise, run your handoff_judge to validate
    result = await Runner.run(
        # handoff_judge,
        output,
        context=ctx.context
    )
    verdict: TriageOutputGuard = result.final_output

    print(f"### Triage Output Guardrail: ")
    # 3️⃣ Return tripwire only if invalid
    return GuardrailFunctionOutput(
        output_info=verdict,
        tripwire_triggered=not verdict.valid_handoff

    )