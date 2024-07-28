from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from shinywidgets import render_plotly, render_widget
from shiny.express import input, render, ui
from shiny import reactive, render

df = pd.read_csv(r'C:\Users\wojci\PycharmProjects\YouTubeAPI\data\processed_video_stats.csv')


# df2 = pd.read_csv(r'C:\Users\wojci\PycharmProjects\YouTubeAPI\data\channel_stats.csv')


def string_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def filter_by_date(df: pd.DataFrame, date_range: tuple):
    rng = sorted(date_range)
    dates = pd.to_datetime(df["date"], format="%Y-%m-%d").dt.date
    return df[(dates >= rng[0]) & (dates <= rng[1])]


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

@render_plotly
def plot_cumulative_views():
    """
    This function generates a line chart of cumulative views over time from the provided DataFrame.
    """
    filtered_df = df
    filtered_df = filter_by_date(filtered_df, input.date_range())

    fig = go.Figure()

    if input.select() == 'XTB':
        list_df = filtered_df[filtered_df['sponsor'] == 'XTB'].copy()
        fig.add_trace(
            go.Scatter(x=list_df['date'], y=list_df['cumulative_views_XTB'], mode='lines', name='Cumulative Views XTB'))
    elif input.select() == 'No sponsor':
        list_df = filtered_df[filtered_df['sponsor'] == 'No sponsor'].copy()
        fig.add_trace(go.Scatter(x=list_df['date'], y=list_df['cumulative_views_No_sponsor'], mode='lines',
                                 name='Cumulative Views No Sponsor'))
    else:
        fig.add_trace(
            go.Scatter(x=filtered_df['date'], y=filtered_df['cumulative_views'], mode='lines', name='Cumulative Views'))
        fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['cumulative_views_XTB'], mode='lines',
                                 name='Cumulative Views XTB'))
        fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['cumulative_views_No_sponsor'], mode='lines',
                                 name='Cumulative Views No Sponsor'))

    fig.update_layout(title='Cumulative Views Over Time', xaxis_title='Date', yaxis_title='Cumulative Views')

    return fig


@render_plotly
def plot_time_series_trends():
    """
    This function generates a line chart showing the trends of views, likes, and comments over time from the provided DataFrame.
    """
    filtered_df = df
    filtered_df = filter_by_date(filtered_df, input.date_range())
    if input.select() == 'XTB':
        list_df = filtered_df[filtered_df['sponsor'] == 'XTB'].copy()
    elif input.select() == 'No sponsor':
        list_df = filtered_df[filtered_df['sponsor'] == 'No sponsor'].copy()
    else:
        list_df = filtered_df

    df_melted = list_df.melt(id_vars=['date'], value_vars=['views', 'likes', 'comments'], var_name='Metric',
                        value_name='Count')
    fig = px.line(df_melted, x='date', y='Count', color='Metric', title='Views, Likes, Comments Over Time')
    return fig


@render_plotly
def plot_duration_distribution():
    """
    This function generates a histogram showing the distribution of video durations.
    """
    filtered_df = df
    filtered_df = filter_by_date(filtered_df, input.date_range()).copy()
    if input.select() == 'XTB':
        list_df = filtered_df[filtered_df['sponsor'] == 'XTB'].copy()
    elif input.select() == 'No sponsor':
        list_df = filtered_df[filtered_df['sponsor'] == 'No sponsor'].copy()
    else:
        list_df = filtered_df

    list_df['duration'] = pd.to_numeric(list_df['duration'], errors='coerce')
    fig = px.histogram(filtered_df, x='duration', nbins=50, title='Distribution of Video Durations',
                       labels={'duration': 'Duration (seconds)'})
    fig.update_layout(
        xaxis_title='Duration (seconds)',
        yaxis_title='Number of Videos',
        bargap=0.2,
    )
    return fig


@render_plotly
def plot_top_performing_videos():
    """
    This function generates a bar chart displaying the top 10 performing videos by views, likes, and comments.
    """
    filtered_df = df
    filtered_df = filter_by_date(filtered_df, input.date_range())
    if input.select() == 'XTB':
        list_df = filtered_df[filtered_df['sponsor'] == 'XTB'].copy()
    elif input.select() == 'No sponsor':
        list_df = filtered_df[filtered_df['sponsor'] == 'No sponsor'].copy()
    else:
        list_df = filtered_df

    top_views = list_df.nlargest(10, 'views')
    top_likes = list_df.nlargest(10, 'likes')
    top_comments = list_df.nlargest(10, 'comments')
    top_videos = pd.concat([top_views, top_likes, top_comments]).drop_duplicates().head(10)
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Bar(x=top_videos['title'], y=top_videos['views'], name='Views', marker=dict(color='blue')),
    )
    fig.add_trace(
        go.Bar(x=top_videos['title'], y=top_videos['likes'], name='Likes', marker=dict(color='red')),
    )
    fig.add_trace(
        go.Bar(x=top_videos['title'], y=top_videos['comments'], name='Comments', marker=dict(color='green')),
    )
    fig.update_layout(
        title='Top Performing Videos by Views, Likes, Comments',
        xaxis_title='Video Title',
        yaxis_title='Count',
        barmode='group'
    )
    return fig


@render_plotly
def plot_engagement_analysis():
    """
    This function generates a scatter plot for engagement analysis: likes vs. comments,
    with point sizes indicating views and hover text showing video titles.
    """
    filtered_df = df
    filtered_df = filter_by_date(filtered_df, input.date_range())
    if input.select() == 'XTB':
        list_df = filtered_df[filtered_df['sponsor'] == 'XTB'].copy()
    elif input.select() == 'No sponsor':
        list_df = filtered_df[filtered_df['sponsor'] == 'No sponsor'].copy()
    else:
        list_df = filtered_df

    fig = px.scatter(list_df, x='likes', y='comments', size='views', hover_name='title',
                     title='Engagement Analysis: Likes vs. Comments',
                     labels={'likes': 'Likes', 'comments': 'Comments'},
                     size_max=60)
    fig.update_layout(
        xaxis_title='Likes',
        yaxis_title='Comments',
        hovermode='closest'
    )
    return fig


@render_plotly
def plot_sponsor_impact():
    """
    This function generates a bar chart comparing average views, likes, and comments for sponsored vs. non-sponsored videos.
    """
    filtered_df = df
    filtered_df = filter_by_date(filtered_df, input.date_range())
    if input.select() == 'XTB':
        list_df = filtered_df[filtered_df['sponsor'] == 'XTB'].copy()
    elif input.select() == 'No sponsor':
        list_df = filtered_df[filtered_df['sponsor'] == 'No sponsor'].copy()
    else:
        list_df = filtered_df

    sponsor_impact = list_df.groupby('sponsor').agg({'views': 'mean', 'likes': 'mean', 'comments': 'mean'}).reset_index()
    sponsor_impact_melted = sponsor_impact.melt(id_vars=['sponsor'], value_vars=['views', 'likes', 'comments'],
                                                var_name='Metric', value_name='Average')
    fig = px.bar(sponsor_impact_melted, x='sponsor', y='Average', color='Metric', barmode='group',
                 title='Sponsor Impact on Views, Likes, Comments',
                 labels={'sponsor': 'Sponsor', 'Average': 'Average Count'})
    fig.update_layout(
        xaxis_title='Sponsor Status',
        yaxis_title='Average Count',
        bargap=0.2,
    )
    return fig

