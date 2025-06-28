# dynamic_context.py
from pydantic import BaseModel, Field
from agents import Agent, RunContextWrapper
# Removed unused import: from agents import function_tool

# Define LocalContext class
class LocalContext(BaseModel):
    user_id: str = Field(..., description="Unique user ID")
    name: str = Field(..., description="Name of the context type.")
    query: str = Field(..., description="The user’s main question or topic.")
    has_data_to_summarize: bool = Field(False, description="True if there’s text to summarize.")
    source_type: str = Field("text", description="e.g. 'text', 'link', 'pdf'")
    search_needed: bool = Field(True, description="True to run web search")
    preferred_language: str = Field("en", description="e.g. 'en', 'es'")
    previous_steps: list[str] = Field(default_factory=list, description="Pipeline steps done")
    history: list[dict] = Field(default_factory=list, description="Conversation history")

async def dynamic_context_wrapper(ctx:RunContextWrapper[LocalContext] ,agent:Agent[LocalContext]) -> str:
    """
    Combines static Triage instructions with dynamic LocalContext.

    # 1️⃣ Static instructions
    A dynamic context wrapper that allows agents to access and modify user context.
    This can be used to personalize responses based on user preferences or history.
    
    You are the friendly Triage Agent in a research pipeline. Your job is to route the user correctly.
    1. Step 1: Analyze the user’s request.
    2. Step 2: If it’s a new topic, hand off to Research_Agent
    3. You are a Chatbot, so you can also respond with a simple answer or in a funny context conversation.
    4. You are a Special Greetting Agent, so you can greet the user in a friendly way.
    5. You are a Context Agent, so you can access and modify the user context
    """
    # 2️⃣ Dynamic context
    dynamic = (
        f"Current context snapshot:\n"
        f"- Name: {ctx.context.name}\n"
        f"- Query: {ctx.context.query}\n"
        f"- Has data to summarize: {ctx.context.has_data_to_summarize}\n"
        f"- Source type: {ctx.context.source_type}\n"
        f"- Search needed: {ctx.context.search_needed}\n"
        f"- Preferred language: {ctx.context.preferred_language}\n"
        f"- Previous steps: {', '.join(ctx.context.previous_steps)}\n"
    )
    return dynamic

# Rebuild the model schema
LocalContext.model_rebuild()