from datetime import datetime
from functools import partial
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from faicons import icon_svg
from plotly.subplots import make_subplots
from shiny import render
from shiny.express import input, ui
from shiny.ui import page_navbar
from shinywidgets import render_plotly

data_dir = Path(__file__).parent / 'data'
df_videos = pd.read_csv(data_dir / 'processed_video_stats.csv')
df_channel = pd.read_csv(data_dir / 'channel_stats.csv')


def string_to_date(date_str: str) -> datetime.date:
    """
    Convert a string date to a datetime.date object.

    Args:
        date_str (str): Date as a string in the format 'YYYY-MM-DD'.

    Returns:
        datetime.date: Corresponding date object.
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def filter_by_date(df: pd.DataFrame, date_range: tuple) -> pd.DataFrame:
    """
    Filter the DataFrame by a date range.

    Args:
        df (pd.DataFrame): DataFrame containing a 'date' column.
        date_range (tuple): Tuple containing start and end dates.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    rng = sorted(date_range)
    dates = pd.to_datetime(df["date"], format="%Y-%m-%d").dt.date
    return df[(dates >= rng[0]) & (dates <= rng[1])]


def get_filtered_data(df: pd.DataFrame, date_range: tuple, sponsor: str) -> pd.DataFrame:
    """
    Get the filtered data based on the date range and sponsor.

    Args:
        df (pd.DataFrame): DataFrame to filter.
        date_range (tuple): Date range for filtering.
        sponsor (str): Sponsor filter value.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    df_filtered = filter_by_date(df, date_range)
    if sponsor == 'XTB':
        return df_filtered[df_filtered['sponsor'] == 'XTB']
    elif sponsor == 'No sponsor':
        return df_filtered[df_filtered['sponsor'] == 'No sponsor']
    return df_filtered


ui.page_opts(
    title="Youtube analysis",
    page_fn=partial(page_navbar, id="page", fillable=True),
)

with ui.nav_panel("Analysis"):
    with ui.layout_column_wrap(fill=False):
        with ui.value_box(showcase=icon_svg("child-reaching")):
            "Total subscribers"


            @render.text
            def total_subs():
                total_subscribers = df_channel['subscriberCount'].iloc[0]
                return f"{total_subscribers:,}".replace(',', ' ')
        with ui.value_box(showcase=icon_svg("eye")):
            "Total views"


            @render.text
            def total_views():
                total_views = df_videos['views'].sum()
                return f"{total_views:,}".replace(',', ' ')
        with ui.value_box(showcase=icon_svg("chart-line")):
            "Average views"


            @render.text
            def avg_views():
                average_views = df_videos['views'].mean()
                return f"{average_views:,.0f}".replace(',', ' ')
        with ui.value_box(showcase=icon_svg("hand-point-up")):
            "Engagement Rate"


            @render.text
            def engagement_rate():
                total_views = df_videos['views'].sum()
                total_likes = df_videos['likes'].sum()
                total_comments = df_videos['comments'].sum()
                engagement_rate = (total_likes + total_comments) / total_views * 100
                return f"{engagement_rate:,.2f}%".replace(',', ' ')

    with ui.layout_sidebar():
        with ui.sidebar(bg="#f8f8f8"):
            "Filter options"
            ui.input_slider("date_range", "Filter by date",
                            min=string_to_date('2017-03-04'),
                            max=string_to_date('2024-07-25'),
                            value=[string_to_date(x) for x in ['2017-03-04', '2024-07-25']]
                            )

            ui.input_select(
                "select",
                "Filter by sponsor:",
                {"All": "All", "XTB": "XTB", "No sponsor": "No sponsor"},
            )


        @render_plotly(height='600px')
        def plot_cumulative_views():
            """
            This function generates a line chart of cumulative views over time from the provided DataFrame.
            """
            filtered_df = df_videos
            filtered_df = filter_by_date(filtered_df, input.date_range())

            fig = go.Figure()

            if input.select() == 'XTB':
                list_df = filtered_df[filtered_df['sponsor'] == 'XTB'].copy()
                fig.add_trace(
                    go.Scatter(x=list_df['date'], y=list_df['cumulative_views_XTB'], mode='lines',
                               name='Cumulative Views XTB'))
            elif input.select() == 'No sponsor':
                list_df = filtered_df[filtered_df['sponsor'] == 'No sponsor'].copy()
                fig.add_trace(go.Scatter(x=list_df['date'], y=list_df['cumulative_views_No_sponsor'], mode='lines',
                                         name='Cumulative Views No Sponsor'))
            else:
                fig.add_trace(
                    go.Scatter(x=filtered_df['date'], y=filtered_df['cumulative_views'], mode='lines',
                               name='Cumulative Views'))
                fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['cumulative_views_XTB'], mode='lines',
                                         name='Cumulative Views XTB'))
                fig.add_trace(
                    go.Scatter(x=filtered_df['date'], y=filtered_df['cumulative_views_No_sponsor'], mode='lines',
                               name='Cumulative Views No Sponsor'))

            fig.update_layout(title='Cumulative Views Over Time', xaxis_title='Date', yaxis_title='Cumulative Views')

            return fig


        @render_plotly(height='600px')
        def plot_time_series_trends():
            """
            Generate a line chart showing trends of views, likes, and comments over time.
            """
            filtered_df = get_filtered_data(df_videos, input.date_range(), input.select())
            df_melted = filtered_df.melt(id_vars=['date'], value_vars=['views', 'likes', 'comments'], var_name='Metric',
                                         value_name='Count')
            fig = px.line(df_melted, x='date', y='Count', color='Metric', title='Views, Likes, Comments Over Time')
            return fig


        @render_plotly(height='600px')
        def plot_top_performing_videos():
            """
            Generate a bar chart displaying the top 10 performing videos by views, likes, and comments.
            """
            filtered_df = get_filtered_data(df_videos, input.date_range(), input.select())
            top_views = filtered_df.nlargest(10, 'views')
            top_likes = filtered_df.nlargest(10, 'likes')
            top_comments = filtered_df.nlargest(10, 'comments')
            top_videos = pd.concat([top_views, top_likes, top_comments]).drop_duplicates().head(10)

            # Truncate titles to the first 15 characters
            top_videos['short_title'] = top_videos['title'].str.slice(0, 30) + '...'

            fig = make_subplots(rows=1, cols=1)
            fig.add_trace(
                go.Bar(x=top_videos['short_title'], y=top_videos['views'], name='Views', marker=dict(color='blue')))
            fig.add_trace(
                go.Bar(x=top_videos['short_title'], y=top_videos['likes'], name='Likes', marker=dict(color='red')))
            fig.add_trace(go.Bar(x=top_videos['short_title'], y=top_videos['comments'], name='Comments',
                                 marker=dict(color='green')))
            fig.update_layout(title='Top Performing Videos by Views, Likes, Comments', xaxis_title='Video Title',
                              yaxis_title='Count', barmode='group')
            return fig


        @render_plotly(height='600px')
        def plot_engagement_analysis():
            """
            Generate a scatter plot for engagement analysis: likes vs. comments, with point sizes indicating views and hover text showing video titles.
            """
            filtered_df = get_filtered_data(df_videos, input.date_range(), input.select())
            fig = px.scatter(filtered_df, x='likes', y='comments', size='views', hover_name='title',
                             title='Engagement Analysis: Likes vs. Comments',
                             labels={'likes': 'Likes', 'comments': 'Comments'}, size_max=60)
            fig.update_layout(xaxis_title='Likes', yaxis_title='Comments', hovermode='closest')
            return fig


        with ui.layout_columns():
            @render_plotly(height='600px')
            def plot_sponsor_impact():
                """
                Generate a bar chart comparing average views, likes, and comments for sponsored vs. non-sponsored videos.
                """
                filtered_df = get_filtered_data(df_videos, input.date_range(), input.select())
                sponsor_impact = filtered_df.groupby('sponsor').agg(
                    {'views': 'mean', 'likes': 'mean', 'comments': 'mean'}).reset_index()
                sponsor_impact_melted = sponsor_impact.melt(id_vars=['sponsor'],
                                                            value_vars=['views', 'likes', 'comments'],
                                                            var_name='Metric', value_name='Average')
                fig = px.bar(sponsor_impact_melted, x='sponsor', y='Average', color='Metric', barmode='group',
                             title='Sponsor Impact on Views, Likes, Comments',
                             labels={'sponsor': 'Sponsor', 'Average': 'Average Count'})
                fig.update_layout(xaxis_title='Sponsor Status', yaxis_title='Average Count', bargap=0.2)
                return fig


            @render_plotly(height='600px')
            def plot_duration_distribution():
                """
                Generate a histogram showing the distribution of video durations.
                """
                filtered_df = get_filtered_data(df_videos, input.date_range(), input.select())
                filtered_df['duration'] = pd.to_numeric(filtered_df['duration'], errors='coerce')
                fig = px.histogram(filtered_df, x='duration', nbins=50, title='Distribution of Video Durations',
                                   labels={'duration': 'Duration (seconds)'})
                fig.update_layout(xaxis_title='Duration (seconds)', yaxis_title='Number of Videos', bargap=0.2)
                return fig

with ui.nav_panel("Data"):
    "Data Grid"


    @render.data_frame
    def videos_df():
        return render.DataGrid(df_videos)
