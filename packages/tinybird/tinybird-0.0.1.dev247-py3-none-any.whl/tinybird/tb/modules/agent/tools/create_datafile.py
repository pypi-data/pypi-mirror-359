import difflib
from pathlib import Path

try:
    from colorama import Back, Fore, Style, init

    init()
except ImportError:  # fallback so that the imported classes always exist

    class ColorFallback:
        def __getattr__(self, name):
            return ""

    Fore = Back = Style = ColorFallback()

import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import Datafile, TinybirdAgentContext, show_options
from tinybird.tb.modules.exceptions import CLIBuildException
from tinybird.tb.modules.feedback_manager import FeedbackManager


def create_line_numbered_diff(original_content: str, new_content: str, filename: str) -> str:
    """Create a diff with line numbers similar to the example format"""
    original_lines = original_content.splitlines()
    new_lines = new_content.splitlines()

    # Create a SequenceMatcher to find the differences
    matcher = difflib.SequenceMatcher(None, original_lines, new_lines)

    result = []
    result.append(f"╭{'─' * 88}╮")
    result.append(f"│ {filename:<86} │")
    result.append(f"│{' ' * 88}│")

    # Process the opcodes to build the diff
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            # Show context lines
            for i, line in enumerate(original_lines[i1:i2]):
                line_num = i1 + i + 1
                result.append(f"│ {line_num:4}        {line:<74} │")
        elif tag == "replace":
            # Show removed lines
            for i, line in enumerate(original_lines[i1:i2]):
                line_num = i1 + i + 1
                result.append(f"│ {Back.RED}{line_num:4} -      {line:<74}{Back.RESET} │")
            # Show added lines
            for i, line in enumerate(new_lines[j1:j2]):
                line_num = i1 + i + 1
                result.append(f"│ {Back.GREEN}{line_num:4} +      {line:<74}{Back.RESET} │")
        elif tag == "delete":
            # Show removed lines
            for i, line in enumerate(original_lines[i1:i2]):
                line_num = i1 + i + 1
                result.append(f"│ {Back.RED}{line_num:4} -      {line:<74}{Back.RESET} │")
        elif tag == "insert":
            # Show added lines
            for i, line in enumerate(new_lines[j1:j2]):
                # Use the line number from the original position
                line_num = i1 + i + 1
                result.append(f"│ {Back.GREEN}{line_num:4} +      {line:<74}{Back.RESET} │")

    result.append(f"╰{'─' * 88}╯")
    return "\n".join(result)


def create_line_numbered_content(content: str, filename: str) -> str:
    """Create a formatted display of file content with line numbers"""
    lines = content.splitlines()

    result = []
    result.append(f"╭{'─' * 88}╮")
    result.append(f"│ {filename:<86} │")
    result.append(f"│{' ' * 88}│")

    for i, line in enumerate(lines, 1):
        result.append(f"│ {i:4}        {line:<74} │")

    result.append(f"╰{'─' * 88}╯")
    return "\n".join(result)


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
        resource.pathname = resource.pathname.removeprefix("/")
        path = Path(ctx.deps.folder) / resource.pathname
        content = resource.content
        exists = str(path) in ctx.deps.get_project_files()
        if exists:
            content = create_line_numbered_diff(path.read_text(), resource.content, resource.pathname)
        else:
            content = create_line_numbered_content(resource.content, resource.pathname)
        click.echo(content)
        confirmation = ctx.deps.dangerously_skip_permissions or get_resource_confirmation(resource, exists)

        if not confirmation:
            ctx.deps.thinking_animation.start()
            return f"Resource {resource.pathname} was not created. User cancelled creation."

        folder_path = path.parent
        folder_path.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        path.write_text(resource.content)
        ctx.deps.build_project(test=True, silent=True)
        ctx.deps.thinking_animation.start()
        return f"Created {resource.pathname}"

    except CLIBuildException as e:
        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.error(message=e))
        ctx.deps.thinking_animation.start()
        return f"Error building project: {e}"
    except Exception as e:
        return f"Error creating {resource.pathname}: {e}"
