# Smart Research Assistant

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI_Agents_SDK-0.1.0-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

Smart Research Assistant is an AI-powered application built with the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) to provide a modular, extensible research pipeline. It enables users to input topics, perform web searches, summarize findings, and maintain persistent conversation history, all while leveraging advanced agent orchestration and lifecycle management. The project showcases approximately 90% of the OpenAI Agents SDK's capabilities, including agents, runners, lifecycle hooks, guardrails, handoffs, and context management.

## Table of Contents

- [Features](#features)
- [OpenAI Agents SDK Utilization](#openai-agents-sdk-utilization)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Usage](#usage)
- [Lifecycle Hooks](#lifecycle-hooks)
- [Context Management](#context-management)
- [Guardrails](#guardrails)
- [Handoffs](#handoffs)
- [File Handling and Resumption](#file-handling-and-resumption)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multi-Agent Pipeline**: Includes `Triage_Agent`, `Research_Agent`, and `Summary_Agent` for task routing, web searching, and result summarization.
- **Persistent Conversations**: Saves and resumes user conversations using JSON files, ensuring continuity even after interruptions (e.g., system crashes or network issues).
- **Lifecycle Hooks**: Comprehensive `RunHooks` and `AgentHooks` implementations to monitor and log runner and agent events (e.g., start, end, exceptions, handoffs).
- **Guardrails**: Input and output guardrails to filter inappropriate or unsafe content.
- **Asynchronous Operations**: Uses `aiofiles` for non-blocking file I/O and async event handling for efficient performance.
- **Cross-Platform Compatibility**: Utilizes `pathlib` for robust file handling across operating systems.
- **Modular Design**: Easily extensible with additional agents, tools, or guardrails.

## OpenAI Agents SDK Utilization

This project leverages approximately 90% of the OpenAI Agents SDK's features (as of June 2025), including:

1. **Agents**:
   - Defines multiple agents (`Triage_Agent`, `Research_Agent`, `Summary_Agent`) with specific roles.
   - Uses `Agent[LocalContext]` for type-safe context management.
   - Configures agents with custom instructions, tools, and handoffs.

2. **Runners**:
   - Utilizes `Runner` with `run_streamed` for asynchronous event streaming.
   - Supports lifecycle hooks via the `hooks` parameter.

3. **Lifecycle Hooks**:
   - Implements `RunHooks` for runner events (`on_run_start`, `on_run_end`, `on_run_exception`).
   - Implements `AgentHooks` for agent events (`on_agent_start`, `on_agent_end`, `on_agent_exception`, `on_handoff`, `on_tool_call`, `on_tool_result`, `on_message`, `on_thought`, `on_action`).
   - Tracks event counts and logs usage data (e.g., token counts via `RunContextWrapper.usage`).

4. **Context Management**:
   - Uses `LocalContext` (Pydantic-based) to store user data, query, and conversation history.
   - Integrates dynamic context via `dynamic_context_wrapper` for personalized agent responses.

5. **Handoffs**:
   - Configures agent handoffs (e.g., `Triage_Agent` to `Research_Agent`) with custom tool names and descriptions.
   - Uses `handoff_filters` for input processing during handoffs.

6. **Guardrails**:
   - Implements input and output guardrails (`triage_agent_guardrail`, `research_input_guardrail`, etc.) to ensure safe and relevant interactions.
   - Handles `InputGuardrailTripwireTriggered` and `OutputGuardrailTripwireTriggered` exceptions.

7. **Tools**:
   - Integrates a `search_web` tool for `Research_Agent` to fetch real-time web data.

8. **Event Streaming**:
   - Processes streamed events (`agent_updated_stream_event`, `run_item_stream_event`) for real-time feedback.

*Note*: Features like advanced analytics or certain experimental SDK components (if any) are not fully utilized but can be extended as needed.

## Project Structure

```
Smart-Research-Assistant/
├── Context/
│   └── dynamic.py        # Defines LocalContext and dynamic_context_wrapper
├── Guardrails/
│   ├── Triage_guardrails.py    # Triage agent guardrails
│   ├── research_guardrails.py  # Research agent guardrails
│   └── summary_guardrail.py    # Summary agent guardrails
├── LifeCycle/
│   ├── runnerlifecycle.py      # RunHooks and AgentHooks implementations
│   └── agents_types.py         # Type imports for lifecycle classes
├── main.py               # Main application logic with agent definitions
├── project.py            # Enhanced async function for conversation management
├── project_with_resumption.py  # Alternative with conversation resumption
├── search_tool.py        # Web search tool for Research_Agent
├── .env                  # Environment variables (e.g., GEMINI_API_KEY)
└── README.md             # Project documentation
```

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/Smart-Research-Assistant.git
   cd Smart-Research-Assistant
   ```

2. **Install Dependencies**:
   Ensure Python 3.8+ is installed. Use a virtual environment and install requirements:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install openai-agents aiofiles pydantic
   ```

3. **Set Environment Variables**:
   Create a `.env` file with your API key:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

4. **Verify Files**:
   Ensure all files (`main.py`, `project.py`, `Context/dynamic.py`, etc.) are in place as per the project structure.

## Usage

1. **Run the Application**:
   Use the `project_with_resumption.py` script for persistent conversations:
   ```bash
   python project_with_resumption.py
   ```

2. **Interact with the Assistant**:
   - Enter a `user_id` (e.g., `user1`) and `name` (e.g., `Alice`).
   - For existing users, the previous conversation history will be displayed.
   - Input a topic (e.g., `test topic`) or `exit` to quit.
   - The assistant processes queries, performs searches, and summarizes results.

3. **Example Output**:
   ```
   Enter your user ID: user1
   Enter your name: Alice
   Resumed context for user user1
   Previous conversation:
   User: test topic
   Assistant: Current context snapshot: ...
   Enter topic or 'exit': new topic
   === Run starting ===
   Runner started
   Agent Triage_Agent started
   Agent updated: Triage_Agent
   -- Message output:
   Current context snapshot:
   - User ID: user1
   - Name: Alice
   - Query: new topic
   ...
   Runner finished
   Context saved to context_user1.json
   === Run complete ===
   ```

4. **Conversation Files**:
   - Conversations are saved in `context_{user_id}.json` (e.g., `context_user1.json`).
   - Each file stores the `LocalContext` with user data and history.

## Lifecycle Hooks

The project implements comprehensive lifecycle hooks for both runners and agents, leveraging `RunHooks` and `AgentHooks` from the OpenAI Agents SDK:

- **RunHooks** (`LifeCycle/runnerlifecycle.py`):
  - `on_run_start`: Logs when a runner starts.
  - `on_run_end`: Logs the output and saves context to a file.
  - `on_run_exception`: Handles runner errors.
  - Tracks event counts and usage data (e.g., tokens).

- **AgentHooks** (`LifeCycle/runnerlifecycle.py`):
  - `on_agent_start`, `on_agent_end`, `on_agent_exception`: Monitor agent lifecycle.
  - `on_handoff`, `on_tool_call`, `on_tool_result`, `on_message`, `on_thought`, `on_action`: Track agent-specific events like handoffs and tool usage.
  - Handles `from_agent` and `context` parameters for robustness.

Example:
```python
# In main.py
runner_lifecycle = MyRunnerLifecycle()
runner = Runner(hooks=runner_lifecycle)
agent = Agent(name="Triage_Agent", hooks=MyAgentLifecycle(), ...)
```

## Context Management

- **LocalContext** (`Context/dynamic.py`):
  - A Pydantic model storing `user_id`, `name`, `query`, `history`, and other metadata.
  - Serialized to JSON using `model_dump()` for file storage.
  - Example:
    ```json
    {
      "user_id": "user1",
      "name": "Alice",
      "query": "test topic",
      "history": [
        {"role": "user", "content": "test topic"},
        {"role": "assistant", "content": "Response..."}
      ]
    }
    ```

- **Dynamic Context** (`dynamic_context_wrapper`):
  - Generates dynamic instructions based on `LocalContext` for personalized agent responses.

## Guardrails

- **Input Guardrails**: Filter user inputs to prevent inappropriate or harmful queries.
- **Output Guardrails**: Ensure agent responses are safe and relevant.
- **Implementation**: Defined in `Guardrails/` (e.g., `triage_agent_guardrail`, `research_output_guardrail`).
- **Error Handling**: Catches `InputGuardrailTripwireTriggered` and `OutputGuardrailTripwireTriggered` exceptions.

## Handoffs

- **Agent Handoffs**: `Triage_Agent` can hand off to `Research_Agent` or `Summary_Agent` using the `handoff` function.
- **Configuration**: Custom tool names and descriptions (e.g., `go_research` for `Research_Agent`).
- **Filters**: Uses `handoff_filters.remove_all_tools` to process inputs during handoffs.

Example:
```python
# In main.py
Triage_Agent = Agent[LocalContext](
    name="Triage_Agent",
    handoffs=[handoff(agent=research_Agent, tool_name_override="go_research", ...)],
    ...
)
```

## File Handling and Resumption

- **File Storage**: Conversations are saved asynchronously using `aiofiles` to `context_{user_id}.json`.
- **Unique Files**: `project.py` enforces unique `user_id`s, prompting for a new ID if a file exists.
- **Resumption**: `project_with_resumption.py` loads existing files and displays conversation history, allowing seamless continuation after interruptions.
- **Error Handling**: Robust checks for file permissions, JSON parsing, and Pydantic validation.

Example:
```python
# In project_with_resumption.py
if context_file.exists():
    context = await load_context(context_file)
    print(f"Resumed context for user {user_id}")
    if context.history:
        print("\nPrevious conversation:")
        for msg in context.history:
            print(f"{msg['role'].capitalize()}: {msg['content']}")
```

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please ensure tests pass and follow the coding style in the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.