import sys
from datetime import datetime

import click
from prompt_toolkit import prompt
from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.styles import Style
from pydantic_ai import Agent, Tool
from pydantic_ai.messages import ModelMessage

from tinybird.prompts import (
    connection_instructions,
    copy_pipe_instructions,
    datasource_example,
    datasource_instructions,
    gcs_connection_example,
    kafka_connection_example,
    materialized_pipe_instructions,
    pipe_example,
    pipe_instructions,
    s3_connection_example,
    sink_pipe_instructions,
)
from tinybird.tb.modules.agent.banner import display_banner
from tinybird.tb.modules.agent.client import TinybirdClient
from tinybird.tb.modules.agent.memory import clear_history, load_history
from tinybird.tb.modules.agent.models import create_model
from tinybird.tb.modules.agent.prompts import datafile_instructions, plan_instructions, sql_instructions
from tinybird.tb.modules.agent.tools.create_datafile import create_datafile
from tinybird.tb.modules.agent.tools.explore import explore_data
from tinybird.tb.modules.agent.tools.plan import plan
from tinybird.tb.modules.agent.tools.preview_datafile import preview_datafile
from tinybird.tb.modules.agent.utils import TinybirdAgentContext
from tinybird.tb.modules.feedback_manager import FeedbackManager


class TinybirdAgent:
    def __init__(self, token: str, host: str, folder: str):
        self.token = token
        self.host = host
        self.folder = folder
        self.messages: list[ModelMessage] = []
        self.agent = Agent(
            model=create_model(token, host),
            deps_type=TinybirdAgentContext,
            system_prompt=f"""
You are a Tinybird Code, an agentic CLI that can help users to work with Tinybird.

You are an interactive CLI tool that helps users with data engineering tasks. Use the instructions below and the tools available to you to assist the user.

# Tone and style
You should be concise, direct, and to the point. 
Remember that your output will be displayed on a command line interface. Your responses can use Github-flavored markdown for formatting.
Output text to communicate with the user; all text you output outside of tool use is displayed to the user. Only use tools to complete tasks. Never use tools like Bash or code comments as means to communicate with the user during the session.
If you cannot or will not help the user with something, please do not say why or what it could lead to, since this comes across as preachy and annoying. Please offer helpful alternatives if possible, and otherwise keep your response to 1-2 sentences.
IMPORTANT: You should minimize output tokens as much as possible while maintaining helpfulness, quality, and accuracy. Only address the specific query or task at hand, avoiding tangential information unless absolutely critical for completing the request. If you can answer in 1-3 sentences or a short paragraph, please do.
IMPORTANT: You should NOT answer with unnecessary preamble or postamble (such as explaining your code or summarizing your action), unless the user asks you to.
IMPORTANT: Keep your responses short, since they will be displayed on a command line interface. You MUST answer concisely with fewer than 4 lines (not including tool use or code generation), unless user asks for detail. Answer the user's question directly, without elaboration, explanation, or details. One word answers are best. Avoid introductions, conclusions, and explanations. You MUST avoid text before/after your response, such as "The answer is <answer>.", "Here is the content of the file..." or "Based on the information provided, the answer is..." or "Here is what I will do next...". Here are some examples to demonstrate appropriate verbosity:

# Proactiveness
You are allowed to be proactive, but only when the user asks you to do something. You should strive to strike a balance between:
Doing the right thing when asked, including taking actions and follow-up actions
Not surprising the user with actions you take without asking
For example, if the user asks you how to approach something, you should do your best to answer their question first, and not immediately jump into taking actions.
Do not add additional code explanation summary unless requested by the user. After working on a file, just stop, rather than providing an explanation of what you did.

# Code style
IMPORTANT: DO NOT ADD ANY COMMENTS unless asked by the user.

# Tools
You have access to the following tools:
1. `explore_data` - Explore data in the current workspace
2. `preview_datafile` - Preview the content of a datafile (datasource, endpoint, materialized, sink, copy, connection).
3. `create_datafile` - Create a file in the project folder. Confirmation will be asked by the tool before creating the file.
4. `plan` - Plan the creation or update of resources.


# When creating or updating datafiles:
1. Use `plan` tool to plan the creation or update of resources.
2. If the user confirms the plan, go from 3 to 7 steps until all the resources are created, updated or skipped.
3. Use `preview_datafile` tool to preview the content of a datafile.
4. Without asking, use the `create_datafile` tool to create the datafile, because it will ask for confirmation before creating the file.
5. Check the result of the `create_datafile` tool to see if the datafile was created successfully.
6. If the datafile was created successfully, report the result to the user.
7. If the datafile was not created successfully, finish the process and just wait for a new user prompt.

IMPORTANT: If the user cancels some of the steps or there is an error, DO NOT continue with the plan. Stop the process and wait for the user before using any other tool.

# When planning the creation or update of resources:
{plan_instructions}
{datafile_instructions}

# Working with datasource files:
{datasource_instructions}
{datasource_example}

# Working with any type of pipe file:
{pipe_instructions}
{pipe_example}

# Working with materialized pipe files:
{materialized_pipe_instructions}

# Working with sink pipe files:
{sink_pipe_instructions}

# Working with copy pipe files:
{copy_pipe_instructions}

# Working with SQL queries:
{sql_instructions}

# Working with connections files:
{connection_instructions}

# Connection examples:
Kafka: {kafka_connection_example}
S3: {s3_connection_example}
GCS: {gcs_connection_example}

# Info
Today is {datetime.now().strftime("%Y-%m-%d")}
""",
            tools=[
                Tool(explore_data, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(preview_datafile, docstring_format="google", require_parameter_descriptions=True, takes_ctx=False),
                Tool(create_datafile, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(plan, docstring_format="google", require_parameter_descriptions=True, takes_ctx=False),
            ],
        )

    def _keep_recent_messages(self) -> list[ModelMessage]:
        """Keep only the last 5 messages to manage token usage."""
        return self.messages[-5:] if len(self.messages) > 5 else self.messages

    def run(self, user_prompt: str) -> None:
        result = self.agent.run_sync(
            user_prompt,
            deps=TinybirdAgentContext(
                client=TinybirdClient(token=self.token, host=self.host),
                folder=self.folder,
            ),
            message_history=self.messages,
        )
        new_messages = result.new_messages()
        self.messages.extend(new_messages)
        click.echo("\n")
        click.echo(result.output)
        click.echo("\n")


def run_agent(token: str, host: str, folder: str):
    display_banner()

    try:
        agent = TinybirdAgent(token, host, folder)
        click.echo()
        click.echo(FeedbackManager.success(message="Welcome to Tinybird Code"))
        click.echo(FeedbackManager.info(message="Describe what you want to create and I'll help you build it"))
        click.echo(FeedbackManager.info(message="Commands: 'exit', 'quit', 'help', or Ctrl+C to exit"))
        click.echo()

    except Exception as e:
        click.echo(FeedbackManager.error(message=f"Failed to initialize agent: {e}"))
        return

    # Interactive loop
    try:
        while True:
            try:
                user_input = prompt(
                    [("class:prompt", "tb » ")],
                    history=load_history(),
                    cursor=CursorShape.BLOCK,
                    style=Style.from_dict(
                        {
                            "prompt": "#40a8a8 bold",
                            "": "",  # Normal color for user input
                        }
                    ),
                )

                if user_input.lower() in ["exit", "quit"]:
                    click.echo(FeedbackManager.info(message="Goodbye!"))
                    break
                elif user_input.lower() == "clear":
                    clear_history()
                    continue
                elif user_input.lower() == "help":
                    click.echo()
                    click.echo(FeedbackManager.info(message="Tinybird Code Help:"))
                    click.echo("• Describe what you want to create: 'Create a user analytics system'")
                    click.echo("• Ask for specific resources: 'Create a pipe to aggregate daily clicks'")
                    click.echo("• Request data sources: 'Set up a Kafka connection for events'")
                    click.echo("• Type 'exit' or 'quit' to leave")
                    click.echo()
                    continue
                elif user_input.strip() == "":
                    continue
                else:
                    agent.run(user_input)

            except KeyboardInterrupt:
                click.echo(FeedbackManager.info(message="Goodbye!"))
                break
            except EOFError:
                click.echo(FeedbackManager.info(message="Goodbye!"))
                break

    except Exception as e:
        click.echo(FeedbackManager.error(message=f"Error: {e}"))
        sys.exit(1)
