from pathlib import Path

import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import Datafile, TinybirdAgentContext, show_options


def get_resource_confirmation(resource: Datafile) -> bool:
    """Get user confirmation for creating a resource"""
    while True:
        result = show_options(
            options=[f"Yes, create {resource.type} '{resource.name}'", "No, and tell Tinybird Code what to do"],
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
        click.echo()
        click.echo(resource.content)
        confirmation = get_resource_confirmation(resource)

        if not confirmation:
            return f"Resource {resource.pathname} was not created. User cancelled creation."

        resource.pathname = resource.pathname.removeprefix("/")

        path = Path(ctx.deps.folder) / resource.pathname

        folder_path = path.parent

        if not folder_path.exists():
            folder_path.mkdir()

        if not path.exists():
            path.touch()

        path.write_text(resource.content)

        return f"Created {resource.pathname}"

    except Exception as e:
        return f"Error creating {resource.pathname}: {e}"
