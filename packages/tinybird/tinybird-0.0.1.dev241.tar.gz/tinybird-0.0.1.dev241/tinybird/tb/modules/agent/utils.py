import os
from contextlib import contextmanager
from typing import Any, Callable, List, Optional

import click
from prompt_toolkit.application import Application, get_app
from prompt_toolkit.filters import IsDone
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.patch_stdout import patch_stdout as pt_patch_stdout
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.styles import Style
from pydantic import BaseModel, Field


class TinybirdAgentContext(BaseModel):
    explore_data: Callable[[str], str]
    folder: str


default_style = Style.from_dict(
    {
        "separator": "#6C6C6C",
        "questionmark": "#FF9D00 bold",
        "selected": "#5F819D",
        "pointer": "#FF9D00 bold",
        "instruction": "",  # default
        "answer": "#5F819D bold",
        "question": "",
    }
)


def if_mousedown(handler):
    def handle_if_mouse_down(mouse_event):
        if mouse_event.event_type == MouseEventType.MOUSE_DOWN:
            return handler(mouse_event)
        else:
            return NotImplemented

    return handle_if_mouse_down


class Separator:
    line = "-" * 15

    def __init__(self, line=None):
        if line:
            self.line = line

    def __str__(self):
        return self.line


class PromptParameterException(ValueError):
    def __init__(self, message, errors=None):
        # Call the base class constructor with the parameters it needs
        super().__init__("You must provide a `%s` value" % message, errors)


class InquirerControl(FormattedTextControl):
    def __init__(self, choices, default, **kwargs):
        self.selected_option_index = 0
        self.answered = False
        self.choices = choices
        self._init_choices(choices, default)
        super().__init__(self._get_choice_tokens, **kwargs)

    def _init_choices(self, choices, default):
        # helper to convert from question format to internal format
        self.choices = []  # list (name, value, disabled)
        searching_first_choice = True
        for i, c in enumerate(choices):
            if isinstance(c, Separator):
                self.choices.append((c, None, None))
            else:
                if isinstance(c, str):
                    self.choices.append((c, c, None))
                else:
                    name = c.get("name")
                    value = c.get("value", name)
                    disabled = c.get("disabled", None)
                    self.choices.append((name, value, disabled))
                    if value == default:
                        self.selected_option_index = i
                        searching_first_choice = False
                if searching_first_choice:
                    self.selected_option_index = i  # found the first choice
                    searching_first_choice = False
                if default and (default in (i, c)):
                    self.selected_option_index = i  # default choice exists
                    searching_first_choice = False

    @property
    def choice_count(self):
        return len(self.choices)

    def _get_choice_tokens(self):
        tokens: list[Any] = []

        def append(index, choice):
            selected = index == self.selected_option_index

            @if_mousedown
            def select_item(mouse_event):
                # bind option with this index to mouse event
                self.selected_option_index = index
                self.answered = True
                get_app().exit(result=self.get_selection()[0])

            if isinstance(choice[0], Separator):
                tokens.append(("class:separator", "  %s\n" % choice[0]))
            else:
                tokens.append(
                    (
                        "",
                        " \u276f " if selected else "   ",
                    )
                )
                if selected:
                    tokens.append(("[SetCursorPosition]", ""))
                if choice[2]:  # disabled
                    tokens.append(
                        (
                            "",
                            "- %s (%s)" % (choice[0], choice[2]),
                        )
                    )
                else:
                    try:
                        tokens.append(
                            (
                                "",
                                str(choice[0]),
                                select_item,
                            )
                        )
                    except Exception:
                        tokens.append(
                            (
                                "",
                                choice[0],
                                select_item,
                            )
                        )
                tokens.append(("", "\n"))

        # prepare the select choices
        for i, choice in enumerate(self.choices):
            append(i, choice)
        tokens.pop()  # Remove last newline.
        return tokens

    def get_selection(self):
        return self.choices[self.selected_option_index]


def prompt_question(message, **kwargs):
    # TODO disabled, dict choices
    if "choices" not in kwargs:
        raise PromptParameterException("choices")

    choices = kwargs.pop("choices", None)
    default = kwargs.pop("default", None)
    style = kwargs.pop("style", default_style)

    ic = InquirerControl(choices, default=default)

    def get_prompt_tokens():
        tokens = []

        tokens.append(("class:question", " %s " % message))
        if ic.answered:
            tokens.append(("class:answer", " " + ic.get_selection()[0]))
        else:
            tokens.append(("class:instruction", " (Use arrow keys)"))
        return tokens

    # assemble layout
    layout = HSplit(
        [
            Window(height=D.exact(1), content=FormattedTextControl(get_prompt_tokens)),
            ConditionalContainer(Window(ic), filter=~IsDone()),
        ]
    )

    # key bindings
    kb = KeyBindings()

    @kb.add("c-q", eager=True)
    @kb.add("c-c", eager=True)
    def _(event):
        raise KeyboardInterrupt()
        # event.app.exit(result=None)

    @kb.add("down", eager=True)
    def move_cursor_down(event):
        def _next():
            ic.selected_option_index = (ic.selected_option_index + 1) % ic.choice_count

        _next()
        while isinstance(ic.choices[ic.selected_option_index][0], Separator) or ic.choices[ic.selected_option_index][2]:
            _next()

    @kb.add("up", eager=True)
    def move_cursor_up(event):
        def _prev():
            ic.selected_option_index = (ic.selected_option_index - 1) % ic.choice_count

        _prev()
        while isinstance(ic.choices[ic.selected_option_index][0], Separator) or ic.choices[ic.selected_option_index][2]:
            _prev()

    @kb.add("enter", eager=True)
    def set_answer(event):
        ic.answered = True
        event.app.exit(result=ic.get_selection()[1])

    return Application(layout=Layout(layout), key_bindings=kb, mouse_support=True, style=style)


def prompt(questions, answers=None, **kwargs):
    if isinstance(questions, dict):
        questions = [questions]
    answers = answers or {}

    patch_stdout = kwargs.pop("patch_stdout", False)
    kbi_msg = kwargs.pop("keyboard_interrupt_msg", "Cancelled by user")
    raise_kbi = kwargs.pop("raise_keyboard_interrupt", False)

    for question in questions:
        # import the question
        if "type" not in question:
            raise PromptParameterException("type")
        if "name" not in question:
            raise PromptParameterException("name")
        if "message" not in question:
            raise PromptParameterException("message")
        try:
            choices = question.get("choices")
            if choices is not None and callable(choices):
                question["choices"] = choices(answers)

            _kwargs = {}
            _kwargs.update(kwargs)
            _kwargs.update(question)
            type_ = _kwargs.pop("type")
            name = _kwargs.pop("name")
            message = _kwargs.pop("message")
            when = _kwargs.pop("when", None)
            filter = _kwargs.pop("filter", None)

            if when:
                # at least a little sanity check!
                if callable(question["when"]):
                    try:
                        if not question["when"](answers):
                            continue
                    except Exception as e:
                        raise ValueError("Problem in 'when' check of %s question: %s" % (name, e))
                else:
                    raise ValueError("'when' needs to be function that accepts a dict argument")
            if filter and not callable(question["filter"]):
                raise ValueError("'filter' needs to be function that accepts an argument")

            if callable(question.get("default")):
                _kwargs["default"] = question["default"](answers)

            with pt_patch_stdout() if patch_stdout else _dummy_context_manager():
                result = prompt_question(message, **_kwargs)

                if isinstance(result, PromptSession):
                    answer = result.prompt()
                elif isinstance(result, Application):
                    answer = result.run()
                else:
                    # assert isinstance(answer, str)
                    answer = result

                # answer = application.run(
                #    return_asyncio_coroutine=return_asyncio_coroutine,
                #    true_color=true_color,
                #    refresh_interval=refresh_interval)

            if answer is not None:
                if filter:
                    try:
                        answer = question["filter"](answer)
                    except Exception as e:
                        raise ValueError("Problem processing 'filter' of %s question: %s" % (name, e))
                answers[name] = answer
        except AttributeError:
            raise ValueError("No question type '%s'" % type_)
        except KeyboardInterrupt as exc:
            if raise_kbi:
                raise exc from None
            if kbi_msg:
                click.echo(kbi_msg)
            return {}
    return answers


@contextmanager
def _dummy_context_manager():
    yield


def show_options(options: List[str], title: str = "Select an option") -> Optional[str]:
    questions = [
        {
            "type": "list",
            "name": "option",
            "message": title,
            "choices": options,
        }
    ]
    result = prompt(questions)

    if "option" not in result:
        return None

    return result["option"]


def load_existing_resources(folder: str) -> str:
    """Load existing Tinybird resources from the workspace"""
    existing_resources = []

    # Check for datasources
    datasources_dir = os.path.join(folder, "datasources")
    if os.path.exists(datasources_dir):
        for file in os.listdir(datasources_dir):
            if file.endswith(".datasource"):
                file_path = os.path.join(datasources_dir, file)
                try:
                    with open(file_path, "r") as f:
                        existing_resources.append(f"DATASOURCE {file}:\n{f.read()}\n")
                except Exception as e:
                    click.echo(f"Warning: Could not read {file_path}: {e}")

    # Check for pipes
    pipes_dir = os.path.join(folder, "pipes")
    if os.path.exists(pipes_dir):
        for file in os.listdir(pipes_dir):
            if file.endswith(".pipe"):
                file_path = os.path.join(pipes_dir, file)
                try:
                    with open(file_path, "r") as f:
                        existing_resources.append(f"PIPE {file}:\n{f.read()}\n")
                except Exception as e:
                    click.echo(f"Warning: Could not read {file_path}: {e}")

    # Check for connections
    connections_dir = os.path.join(folder, "connections")
    if os.path.exists(connections_dir):
        for file in os.listdir(connections_dir):
            if file.endswith(".connection"):
                file_path = os.path.join(connections_dir, file)
                try:
                    with open(file_path, "r") as f:
                        existing_resources.append(f"CONNECTION {file}:\n{f.read()}\n")
                except Exception as e:
                    click.echo(f"Warning: Could not read {file_path}: {e}")

    return "\n".join(existing_resources)


class Datafile(BaseModel):
    """Represents a generated Tinybird datafile"""

    type: str
    name: str
    content: str
    description: str
    pathname: str
    dependencies: List[str] = Field(default_factory=list)
