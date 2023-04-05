import markdown
import pandas
import plotly.express as px
from plotly.figure_factory import create_table
from ydata_profiling import ProfileReport


class FrameProfilingRenderer:
    """
    Generate a ProfileReport based on a pandas DataFrame
    """

    def __init__(self, title: str = "Pandas Profiling Report"):
        self._title = title

    def to_html(self, df: pandas.DataFrame) -> str:
        assert isinstance(df, pandas.DataFrame)
        profile = ProfileReport(df, title=self._title)
        return profile.to_html()


class MarkdownRenderer:
    """Convert a markdown string to HTML and return HTML as a unicode string.

    This is a shortcut function for `Markdown` class to cover the most
    basic use case.  It initializes an instance of Markdown, loads the
    necessary extensions and runs the parser on the given text.
    """

    def to_html(self, text: str) -> str:
        return markdown.markdown(text)


class BoxRenderer:
    """
    In a box plot, rows of `data_frame` are grouped together into a
    box-and-whisker mark to visualize their distribution.

    Each box spans from quartile 1 (Q1) to quartile 3 (Q3). The second
    quartile (Q2) is marked by a line inside the box. By default, the
    whiskers correspond to the box' edges +/- 1.5 times the interquartile
    range (IQR: Q3-Q1), see "points" for other options.
    """

    # More detail, see https://plotly.com/python/box-plots/
    def __init__(self, column_name):
        self._column_name = column_name

    def to_html(self, df: pandas.DataFrame) -> str:
        fig = px.box(df, y=self._column_name)
        return fig.to_html()


class TableRenderer:
    def to_html(self, df: pandas.DataFrame) -> str:
        fig = create_table(df)
        fig.update_layout(
            autosize=True,
        )
        return fig.to_html()


class GanttChartRenderer:
    def to_html(self, df: pandas.DataFrame) -> str:

        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Part", color="Part")
        fig.update_yaxes(autorange="reversed")
        # fig.update_xaxes(tickformat="%S.%f")  # fig.update_yaxes(autorange="reversed")
        time_dif = df["Finish"].max() - df["Start"].min()

        if time_dif < pandas.Timedelta(seconds=1):
            time_format = "%5f"
        elif time_dif < pandas.Timedelta(minutes=1):
            time_format = "%S:%f"
        elif time_dif < pandas.Timedelta(hours=1):
            time_format = "%M:%S:%f"
        else:
            time_format = "%H:%M:%S:%f"

        fig.update_xaxes(
            tickangle=90,
            tickformat=time_format,
        )

        fig.update_layout(
            autosize=True,
        )

        return fig.to_html()
