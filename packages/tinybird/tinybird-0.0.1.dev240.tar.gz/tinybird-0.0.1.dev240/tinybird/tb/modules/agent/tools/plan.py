import click

from tinybird.tb.modules.agent.utils import show_options


def get_plan_confirmation() -> bool:
    """Get user confirmation for implementing a plan"""
    while True:
        result = show_options(
            options=["Yes, implement the plan", "No, and tell Tinybird Code what to do"],
            title="Do you want to implement the plan?",
        )

        if result is None:  # Cancelled
            return False

        if result.startswith("Yes"):
            return True
        elif result.startswith("No"):
            return False

        return False


def plan(plan: str) -> str:
    """Given a plan, ask the user for confirmation to implement it

    Args:
        plan (str): The plan to implement. Required.

    Returns:
        str: If the plan was implemented or not.
    """
    try:
        click.echo()
        click.echo(plan)
        confirmation = get_plan_confirmation()

        if not confirmation:
            return "Plan was not implemented. User cancelled implementation."

        return "User confirmed the plan. Implementing..."

    except Exception as e:
        return f"Error implementing the plan: {e}"
