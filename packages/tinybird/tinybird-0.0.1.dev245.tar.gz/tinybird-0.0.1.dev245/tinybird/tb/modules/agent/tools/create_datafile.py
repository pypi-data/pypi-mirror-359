from pathlib import Path

import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import Datafile, TinybirdAgentContext, show_options
from tinybird.tb.modules.exceptions import CLIBuildException
from tinybird.tb.modules.feedback_manager import FeedbackManager


def get_resource_confirmation(resource: Datafile, exists: bool) -> bool:
    """Get user confirmation for creating a resource"""
    while True:
        action = "create" if not exists else "update"
        result = show_options(
            options=[f"Yes, {action} {resource.type} '{resource.name}'", "No, and tell Tinybird Code what to do"],
            title=f"What would you like to do with {resource.type} '{resource.name}'?",
        )

        if result is None:  # Cancelled
            return False

        if result.startswith("Yes"):
            return True
        elif result.startswith("No"):
            return False

        return False


def create_datafile(ctx: RunContext[TinybirdAgentContext], resource: Datafile) -> str:
    """Given a resource representation, create a file in the project folder

    Args:
        resource (Datafile): The resource to create. Required.

    Returns:
        str: If the resource was created or not.
    """
    try:
        ctx.deps.thinking_animation.stop()
        click.echo(resource.content)
        resource.pathname = resource.pathname.removeprefix("/")
        path = Path(ctx.deps.folder) / resource.pathname
        exists = str(path) in ctx.deps.get_project_files()
        confirmation = get_resource_confirmation(resource, exists)
        ctx.deps.thinking_animation.start()

        if not confirmation:
            return f"Resource {resource.pathname} was not created. User cancelled creation."

        folder_path = path.parent
        folder_path.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)

        path.write_text(resource.content)
        ctx.deps.build_project()
        return f"Created {resource.pathname}"

    except CLIBuildException as e:
        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.error(message=e))
        ctx.deps.thinking_animation.start()
        return f"Error building project: {e}"
    except Exception as e:
        return f"Error creating {resource.pathname}: {e}"
