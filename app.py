from functools import partial
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from faicons import icon_svg
from shiny import render
from shiny.express import input, ui
from shiny.ui import page_navbar
from shinywidgets import render_plotly

from utils.helpers import string_to_date, filter_by_date

data_dir = Path(__file__).parent / 'data'
df_videos = pd.read_csv(data_dir / 'processed_video_stats.csv')
df_channel = pd.read_csv(data_dir / 'channel_stats.csv')

ui.page_opts(
    title="Youtube analysis - XTB partnership",
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
                filtered_df = filter_by_date(df_videos, input.date_range())
                total_views = filtered_df['views'].sum()
                return f"{total_views:,}".replace(',', ' ')

        with ui.value_box(showcase=icon_svg("chart-line")):
            "Average views"


            @render.text
            def avg_views():
                filtered_df = filter_by_date(df_videos, input.date_range())
                average_views = filtered_df['views'].mean()
                return f"{average_views:,.0f}".replace(',', ' ')

        with ui.value_box(showcase=icon_svg("hand-point-up")):
            "Engagement Rate"


            @render.text
            def engagement_rate():
                filtered_df = filter_by_date(df_videos, input.date_range())
                total_views = filtered_df['views'].sum()
                total_likes = filtered_df['likes'].sum()
                total_comments = filtered_df['comments'].sum()
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

        with ui.layout_column_wrap(fill=False):
            with ui.card():
                "Cumulative Views Over Time"


                @render_plotly
                def plot_cumulative_views_all():
                    """
                    This function generates a line chart of cumulative views over time for all data.
                    """
                    filtered_df = filter_by_date(df_videos, input.date_range())
                    fig = go.Figure()

                    fig.add_trace(
                        go.Scatter(x=filtered_df['date'], y=filtered_df['cumulative_views'], mode='lines',
                                   name='Cumulative Views', line=dict(color='#1A1B41')))

                    fig.update_layout(
                        title=dict(text='All data', font=dict(color='#1A1B41')),
                        xaxis_title='Date',
                        yaxis_title='Cumulative Views',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                        yaxis=dict(showgrid=True, gridcolor='lightgrey')
                    )
                    return fig


                with ui.layout_column_wrap(width=1 / 2):
                    with ui.card():
                        @render_plotly
                        def plot_cumulative_views_no_sponsor():
                            """
                            This function generates a line chart of cumulative views over time for videos with No sponsor.
                            """
                            filtered_df = filter_by_date(df_videos[df_videos['sponsor'] == 'No sponsor'],
                                                         input.date_range())
                            fig = go.Figure()

                            fig.add_trace(
                                go.Scatter(x=filtered_df['date'], y=filtered_df['cumulative_views_No_sponsor'],
                                           mode='lines',
                                           name='Cumulative Views No Sponsor', line=dict(color='#006E90')))

                            fig.update_layout(
                                title=dict(text='No sponsor', font=dict(color='#006E90')),
                                xaxis_title='Date',
                                yaxis_title='Cumulative Views',
                                plot_bgcolor='rgba(0,0,0,0)',
                                xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                                yaxis=dict(showgrid=True, gridcolor='lightgrey')
                            )
                            return fig

                    with ui.card():
                        @render_plotly
                        def plot_cumulative_views_xtb():
                            """
                            This function generates a line chart of cumulative views over time for videos with XTB sponsor.
                            """
                            filtered_df = filter_by_date(df_videos[df_videos['sponsor'] == 'XTB'], input.date_range())
                            fig = go.Figure()

                            fig.add_trace(
                                go.Scatter(x=filtered_df['date'], y=filtered_df['cumulative_views_XTB'], mode='lines',
                                           name='Cumulative Views XTB', line=dict(color='#B80C09')))

                            fig.update_layout(
                                title=dict(text='XTB', font=dict(color='#B80C09')),
                                xaxis_title='Date',
                                yaxis_title='Cumulative Views',
                                plot_bgcolor='rgba(0,0,0,0)',
                                xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                                yaxis=dict(showgrid=True, gridcolor='lightgrey')
                            )
                            return fig

        with ui.layout_column_wrap(fill=False):
            with ui.card():
                "Top Performing Videos"
                with ui.layout_column_wrap(width=1 / 2):
                    with ui.card():
                        @render_plotly
                        def plot_top_performing_videos_no_sponsor():
                            """
                            Generate a bar chart displaying the top 5 videos by likes per 1000 views and comments per 100 views for videos with No sponsor.
                            """
                            filtered_df = filter_by_date(df_videos[df_videos['sponsor'] == 'No sponsor'],
                                                         input.date_range())
                            filtered_df['likes_per_1000_views'] = filtered_df['likes'] / (filtered_df['views'] / 1000)
                            filtered_df['comments_per_1000_views'] = filtered_df['comments'] / (
                                    filtered_df['views'] / 1000)
                            top_videos = filtered_df.nlargest(5, ['likes_per_1000_views', 'comments_per_1000_views'])

                            # Truncate titles to the first 30 characters
                            top_videos['short_title'] = top_videos['title'].str.slice(0, 30) + '...'

                            fig = go.Figure()
                            fig.add_trace(
                                go.Bar(x=top_videos['short_title'], y=top_videos['likes_per_1000_views'],
                                       name='Likes per 1000 Views', marker=dict(color='#006E90')))
                            fig.add_trace(
                                go.Bar(x=top_videos['short_title'], y=top_videos['comments_per_1000_views'],
                                       name='Comments per 1000 Views', marker=dict(color='#3B8DE6')))

                            fig.update_layout(
                                title=dict(text='No sponsor', font=dict(color='#006E90')),
                                xaxis_title='Video Title',
                                yaxis_title='Rate',
                                barmode='group',
                                plot_bgcolor='rgba(0,0,0,0)',
                                xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                                yaxis=dict(showgrid=True, gridcolor='lightgrey')
                            )
                            return fig

                    with ui.card():
                        @render_plotly
                        def plot_top_performing_videos_xtb():
                            """
                            Generate a bar chart displaying the top 5 videos by likes per 1000 views and comments per 100 views for videos with XTB sponsor.
                            """
                            filtered_df = filter_by_date(df_videos[df_videos['sponsor'] == 'XTB'], input.date_range())
                            filtered_df['likes_per_1000_views'] = filtered_df['likes'] / (filtered_df['views'] / 1000)
                            filtered_df['comments_per_1000_views'] = filtered_df['comments'] / (
                                    filtered_df['views'] / 1000)
                            top_videos = filtered_df.nlargest(5, ['likes_per_1000_views', 'comments_per_1000_views'])

                            # Truncate titles to the first 30 characters
                            top_videos['short_title'] = top_videos['title'].str.slice(0, 30) + '...'

                            fig = go.Figure()
                            fig.add_trace(
                                go.Bar(x=top_videos['short_title'], y=top_videos['likes_per_1000_views'],
                                       name='Likes per 1000 Views', marker=dict(color='#B80C09')))
                            fig.add_trace(
                                go.Bar(x=top_videos['short_title'], y=top_videos['comments_per_1000_views'],
                                       name='Comments per 1000 Views', marker=dict(color='#F38743')))

                            fig.update_layout(
                                title=dict(text='XTB', font=dict(color='#B80C09')),
                                xaxis_title='Video Title',
                                yaxis_title='Rate',
                                barmode='group',
                                plot_bgcolor='rgba(0,0,0,0)',
                                xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                                yaxis=dict(showgrid=True, gridcolor='lightgrey')
                            )
                            return fig

        with ui.layout_column_wrap(fill=False):
            with ui.card():
                "Views, Comments and Likes Distribution"
                with ui.layout_column_wrap(fill=False):
                    with ui.card():
                        @render_plotly
                        def plot_boxplot_views():
                            """
                            Generate a boxplot for views for No sponsor and XTB videos.
                            """
                            filtered_no_sponsor_df = filter_by_date(df_videos[df_videos['sponsor'] == 'No sponsor'],
                                                                    input.date_range())
                            filtered_xtb_df = filter_by_date(df_videos[df_videos['sponsor'] == 'XTB'],
                                                             input.date_range())

                            fig = go.Figure()

                            fig.add_trace(
                                go.Box(y=filtered_no_sponsor_df['views'], name='No sponsor', marker_color='#006E90'))
                            fig.add_trace(
                                go.Box(y=filtered_xtb_df['views'], name='XTB', marker_color='#B80C09'))

                            fig.update_layout(
                                title=dict(text='Views for No sponsor and XTB Videos', font=dict(color='#1A1B41')),
                                yaxis_title='Views',
                                plot_bgcolor='rgba(0,0,0,0)',
                                xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                                yaxis=dict(showgrid=True, gridcolor='lightgrey')
                            )
                            return fig

                    with ui.card():
                        @render_plotly
                        def plot_boxplot_comments():
                            """
                            Generate a boxplot for comments for No sponsor and XTB videos.
                            """
                            filtered_no_sponsor_df = filter_by_date(df_videos[df_videos['sponsor'] == 'No sponsor'],
                                                                    input.date_range())
                            filtered_xtb_df = filter_by_date(df_videos[df_videos['sponsor'] == 'XTB'],
                                                             input.date_range())

                            fig = go.Figure()

                            fig.add_trace(
                                go.Box(y=filtered_no_sponsor_df['comments'], name='No sponsor', marker_color='#006E90'))
                            fig.add_trace(
                                go.Box(y=filtered_xtb_df['comments'], name='XTB', marker_color='#B80C09'))

                            fig.update_layout(
                                title=dict(text='Comments for No sponsor and XTB Videos', font=dict(color='#1A1B41')),
                                yaxis_title='Comments',
                                plot_bgcolor='rgba(0,0,0,0)',
                                xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                                yaxis=dict(showgrid=True, gridcolor='lightgrey')
                            )
                            return fig

                    with ui.card():
                        @render_plotly
                        def plot_boxplot_likes():
                            """
                            Generate a boxplot for likes for No sponsor and XTB videos.
                            """
                            filtered_no_sponsor_df = filter_by_date(df_videos[df_videos['sponsor'] == 'No sponsor'],
                                                                    input.date_range())
                            filtered_xtb_df = filter_by_date(df_videos[df_videos['sponsor'] == 'XTB'],
                                                             input.date_range())

                            fig = go.Figure()

                            fig.add_trace(
                                go.Box(y=filtered_no_sponsor_df['likes'], name='No sponsor', marker_color='#006E90'))
                            fig.add_trace(
                                go.Box(y=filtered_xtb_df['likes'], name='XTB', marker_color='#B80C09'))

                            fig.update_layout(
                                title=dict(text='Likes for No sponsor and XTB Videos', font=dict(color='#1A1B41')),
                                yaxis_title='Likes',
                                plot_bgcolor='rgba(0,0,0,0)',
                                xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                                yaxis=dict(showgrid=True, gridcolor='lightgrey')
                            )
                            return fig

        with ui.layout_column_wrap(fill=False):
            with ui.card():
                "Distribution of video durations"
                with ui.layout_column_wrap(width=1 / 2):
                    with ui.card():
                        @render_plotly
                        def plot_duration_distribution_no_sponsor():
                            """
                            Generate a histogram showing the distribution of video durations for No sponsor data.
                            """
                            filtered_df = filter_by_date(df_videos[df_videos['sponsor'] == 'No sponsor'],
                                                         input.date_range())
                            filtered_df['duration'] = pd.to_numeric(filtered_df['duration'], errors='coerce')
                            fig = px.histogram(filtered_df, x='duration', nbins=50,
                                               title='No Sponsor',
                                               labels={'duration': 'Duration (seconds)'},
                                               color_discrete_sequence=['#006E90'])
                            fig.update_layout(
                                xaxis_title='Duration (seconds)',
                                yaxis_title='Number of Videos',
                                bargap=0.2,
                                plot_bgcolor='rgba(0,0,0,0)',
                                title_font=dict(color='#006E90'),
                                xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                                yaxis=dict(showgrid=True, gridcolor='lightgrey')
                            )
                            return fig

                    with ui.card():
                        @render_plotly
                        def plot_duration_distribution_xtb():
                            """
                            Generate a histogram showing the distribution of video durations for XTB data.
                            """
                            filtered_df = filter_by_date(df_videos[df_videos['sponsor'] == 'XTB'], input.date_range())
                            filtered_df['duration'] = pd.to_numeric(filtered_df['duration'], errors='coerce')
                            fig = px.histogram(filtered_df, x='duration', nbins=50,
                                               title='XTB',
                                               labels={'duration': 'Duration (seconds)'},
                                               color_discrete_sequence=['#B80C09'])
                            fig.update_layout(
                                xaxis_title='Duration (seconds)',
                                yaxis_title='Number of Videos',
                                bargap=0.2,
                                plot_bgcolor='rgba(0,0,0,0)',
                                title_font=dict(color='#B80C09'),
                                xaxis=dict(showgrid=True, gridcolor='lightgrey'),
                                yaxis=dict(showgrid=True, gridcolor='lightgrey')
                            )
                            return fig

with ui.nav_panel("Data"):
    "Data Grid"


    @render.data_frame
    def videos_df():
        filtered_df = filter_by_date(df_videos, input.date_range())
        return render.DataGrid(filtered_df)
