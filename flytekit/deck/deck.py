import contextlib
import datetime
import os
import typing
from typing import Optional

import pandas
from jinja2 import Environment, FileSystemLoader, select_autoescape

from flytekit.core.context_manager import ExecutionParameters, ExecutionState, FlyteContext, FlyteContextManager
from flytekit.loggers import logger

OUTPUT_DIR_JUPYTER_PREFIX = "jupyter"
DECK_FILE_NAME = "deck.html"

try:
    from IPython.core.display import HTML
except ImportError:
    ...


class Deck:
    """
    Deck enable users to get customizable and default visibility into their tasks.

    Deck contains a list of renderers (FrameRenderer, MarkdownRenderer) that can
    generate a html file. For example, FrameRenderer can render a DataFrame as an HTML table,
    MarkdownRenderer can convert Markdown string to HTML

    Flyte context saves a list of deck objects, and we use renderers in those decks to render
    the data and create an HTML file when those tasks are executed

    Each task has a least three decks (input, output, default). Input/output decks are
    used to render tasks' input/output data, and the default deck is used to render line plots,
    scatter plots or markdown text. In addition, users can create new decks to render
    their data with custom renderers.

    .. warning::

        This feature is in beta.

    .. code-block:: python

        iris_df = px.data.iris()

        @task()
        def t1() -> str:
            md_text = '#Hello Flyte##Hello Flyte###Hello Flyte'
            m = MarkdownRenderer()
            s = BoxRenderer("sepal_length")
            deck = flytekit.Deck("demo", s.to_html(iris_df))
            deck.append(m.to_html(md_text))
            default_deck = flytekit.current_context().default_deck
            default_deck.append(m.to_html(md_text))
            return md_text


        # Use Annotated to override default renderer
        @task()
        def t2() -> Annotated[pd.DataFrame, TopFrameRenderer(10)]:
            return iris_df

    """

    def __init__(self, name: str, html: Optional[str] = ""):
        self._name = name
        # self.renderers = renderers if isinstance(renderers, list) else [renderers]
        self._html = html
        FlyteContextManager.current_context().user_space_params.decks.append(self)

    def append(self, html: str) -> "Deck":
        assert isinstance(html, str)
        self._html = self._html + "\n" + html
        return self

    @property
    def name(self) -> str:
        return self._name

    @property
    def html(self) -> str:
        return self._html


class TimeLineDeck(Deck):
    """
    The TimeLineDeck class is designed to render the execution time of each part of a task.
    Unlike deck classe, the conversion of data to HTML is delayed until the html property is accessed.
    This approach is taken because rendering a timeline graph with partial data would not provide meaningful insights.
    Instead, the complete data set is used to create a comprehensive visualization of the execution time of each part of the task.
    """

    def __init__(self, name: str, html: Optional[str] = ""):
        super().__init__(name, html)
        self.time_info = []
        self.shift_time = pandas.Timedelta(microseconds=0)

    def append_time_info(self, info: dict):
        assert isinstance(info, dict)

        millisecond = pandas.Timedelta(microseconds=1000)
        # If the execution time of the wrapped code block is less than 1 millisecond, it will be rounded up to 1 millisecond for visualization purposes only.
        # Additionally, all execution times after it will be shifted to avoid overlapping."
        info["Start"] = info["Start"] + self.shift_time
        info["Finish"] = info["Finish"] + self.shift_time

        millisecond = pandas.Timedelta(microseconds=1000)
        if info["Duration"] < millisecond:
            self.shift_time += millisecond - info["Duration"]
            info["Duration"] = millisecond
            info["Finish"] = info["Start"] + millisecond

        self.time_info.append(info)

    @property
    def html(self) -> str:
        from flytekitplugins.deck.renderer import GanttChartRenderer, TableRenderer

        df = pandas.DataFrame(self.time_info)
        note = """
<p><strong>Note:</strong></p>
<ol>
  <li>If the execution time of the wrapped code block is less than 1 millisecond, it will be rounded up to 1 millisecond for visualization purposes only.
   Additionally, all execution times after it will be shifted to avoid overlapping.</li>
  <li>Users can also measure the execution time of their own code. See here for more <a href="https://docs.flyte.org/projects/flytekit/en/latest/deck.html#measure-execution-time">details</a> (TODO: update the link).</li>
</ol>
        """
        return GanttChartRenderer().to_html(df) + "\n" + TableRenderer().to_html(df) + "\n" + note


@contextlib.contextmanager
def measure_execution_time(name: str):
    """
    A context manager that measures the execution time of the wrapped code block and
    appends the timing information to TimeLineDeck.

    :param name: A string that describes the part of the task being executed.
    """
    start_time = datetime.datetime.utcnow()
    try:
        yield
    finally:
        end_time = datetime.datetime.utcnow()
        time_line_deck = FlyteContextManager.current_context().user_space_params.time_line_deck
        time_line_deck.append_time_info(
            dict(Name=name, Start=start_time, Finish=end_time, Duration=end_time - start_time)
        )


def _ipython_check() -> bool:
    """
    Check if interface is launching from iPython (not colab)
    :return is_ipython (bool): True or False
    """
    is_ipython = False
    try:  # Check if running interactively using ipython.
        from IPython import get_ipython

        if get_ipython() is not None:
            is_ipython = True
    except (ImportError, NameError):
        pass
    return is_ipython


def _get_deck(
    new_user_params: ExecutionParameters, ignore_jupyter: bool = False
) -> typing.Union[str, "IPython.core.display.HTML"]:  # type:ignore
    """
    Get flyte deck html string
    If ignore_jupyter is set to True, then it will return a str even in a jupyter environment.
    """
    deck_map = {deck.name: deck.html for deck in new_user_params.decks}
    raw_html = template.render(metadata=deck_map)
    if not ignore_jupyter and _ipython_check():
        return HTML(raw_html)
    return raw_html


def _output_deck(task_name: str, new_user_params: ExecutionParameters):
    ctx = FlyteContext.current_context()
    if ctx.execution_state.mode == ExecutionState.Mode.TASK_EXECUTION:
        output_dir = ctx.execution_state.engine_dir
    else:
        output_dir = ctx.file_access.get_random_local_directory()
    deck_path = os.path.join(output_dir, DECK_FILE_NAME)
    with open(deck_path, "w") as f:
        f.write(_get_deck(new_user_params, ignore_jupyter=True))
    logger.info(f"{task_name} task creates flyte deck html to file://{deck_path}")


root = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(root, "html")
env = Environment(
    loader=FileSystemLoader(templates_dir),
    # 🔥 include autoescaping for security purposes
    # sources:
    # - https://jinja.palletsprojects.com/en/3.0.x/api/#autoescaping
    # - https://stackoverflow.com/a/38642558/8474894 (see in comments)
    # - https://stackoverflow.com/a/68826578/8474894
    autoescape=select_autoescape(enabled_extensions=("html",)),
)
template = env.get_template("template.html")
