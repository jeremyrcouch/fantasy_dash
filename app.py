import pandas as pd

from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go


def read_data(schedule_url: str, points_url: str) -> (pd.DataFrame, pd.DataFrame):
    """
    Read schedule and points data.
    
    Args:
        schedule_url: str, unique portion for schedule
        points_url: str, unique portion for points
    
    Returns:
        schedule: DataFrame, weekly schedule for season
        points: DataFrame, weekly points for season
    """
    
    SHEETS_URL = 'https://docs.google.com/spreadsheets/d/e/'
    PARAMS = '&single=true&output=csv'
    
    schedule = pd.read_csv(SHEETS_URL + schedule_url + PARAMS)
    points = pd.read_csv(SHEETS_URL + points_url + PARAMS)
    
    return schedule, points


def supplement_points(points_wide: pd.DataFrame, schedule: pd.DataFrame,
                      id_col: str, player_col: str, against_col: str, points_col: str) -> pd.DataFrame:
    """Supplement weekly points data.
    
    Args:
        points_wide: DataFrame, weekly points data
        schedule: DataFrame, schedule information
        id_col: str, name of identifier column
        player_col: str, player column name
        against_col: str, vs column name
        points_col: str, points column name
        
    Returns:
        points: DataFrame, weekly points data supplemented with additional info
    """
    
    points_no_na = points_wide.dropna()
    points = pd.melt(points_no_na, id_vars=[id_col], var_name=player_col, value_name=points_col)
    points = pd.merge(points, schedule, how='left', on=[id_col, player_col])
    points_against = points.loc[:, [id_col, player_col, points_col]]
    points_against = points_against.rename(columns={player_col: against_col,
                                                  points_col: points_col+against_col})
    points = pd.merge(points, points_against, how='left', on=[id_col, against_col])
    points['Won'] = points.loc[:, points_col] > points.loc[:, points_col+against_col]
    
    return points


def rank_points():
    """
    """
    
    pass


def expected_win(points: pd.DataFrame, id_col: str, points_col: str) -> pd.Series:
    """Determine if a win is expected given points for week.
    
    Args:
        points: DataFrame, weekly points data
        id_col: str, name of identifier column
        points_col: str, points column name
        
    Returns:
        ExpectedWin: pd.Series, bool for if win was expected
    """
    
    id_stats = pd.DataFrame(points.groupby(id_col)[points_col].median()).reset_index()
    id_stats = id_stats.rename(columns={points_col: 'WeeklyMedianPoints'})
    points = pd.merge(points, id_stats, how='left', on=[id_col])
    points['ExpectedWin'] = points.loc[:, points_col] > points.loc[:, 'WeeklyMedianPoints']
    
    return points.loc[:, 'ExpectedWin']


def calculate_season_stats(points: pd.DataFrame, player_col: str, points_col: str,
                           against_col: str) -> pd.DataFrame:
    """Calculate seasonal statistics.
    
    Args:
        points: DataFrame, weekly points data
        player_col: str, player column name
        points_col: str, points column name
        against_col: str, vs column name
        
    Returns:
        season: DataFrame, seasonal statistics
    """
    
    season = points.groupby(player_col).agg({points_col: 'sum',
                                             points_col+against_col: 'sum',
                                             'Won': 'sum',
                                             'RankPoints': 'sum',
                                             'ExpectedWin': 'sum'})
    season = season.rename(columns={'Won': 'Wins', 'ExpectedWin': 'ExpectedWins'})
    season = season.round({points_col: 2, points_col+against_col: 2, 'RankPoints': 1})
    season['TotalPoints'] = season.loc[:, 'Wins'] + season.loc[:, 'RankPoints']
    season['Place'] = season.loc[:, 'TotalPoints'].rank(ascending=False)
    season = season.sort_values(by='Place', ascending=True)
    
    col_order = ['Place', player_col, points_col, points_col+against_col,
                 'Wins', 'RankPoints', 'TotalPoints', 'ExpectedWins']
    season = season.reset_index().loc[:, col_order]
    
    return season
	
	
def generate_html_table(df, max_rows=float('Inf')):
    return html.Table([html.Tr([html.Th(col) for col in df.columns])] +
                      [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
                      for i in range(min(len(df), max_rows))])


def generate_dash_table(df, max_rows=float('Inf')):
     return dash_table.DataTable(
                id='season-stats-dash-table',
                columns=[{"name": col, "id": col} for col in df.columns], 
                data=df.to_dict('records'),
                style_table={'maxWidth': '750px'},
                style_cell={'textAlign': 'center'},
                style_as_list_view=True,
                style_header={'fontWeight': 'bold'},
#                style_data_conditional = [{
#                    'if': {
#                        'column_id': 'ExpectedWins',
#                        'filter_query': '{ExpectedWins} > {Wins}'
#                    },
#                    'backgroundColor': '#D1FAC1'
#                },
#                {
#                    'if': {
#                        'column_id': 'ExpectedWins',
#                        'filter_query': '{ExpectedWins} < {Wins}'
#                    },
#                    'backgroundColor': '#FAC7C1'
#                }],
                sort_action="native",
                sort_mode="multi"
            )


def get_matchup_items(players: list, schedule: pd.DataFrame, items: list) -> list:
    """
    """
    
    item_map = {}
    item_index = 0
    for player in players:
        against = schedule.loc[schedule[PLAYER_COL] == player, AGAINST_COL].iloc[0]
        if player not in item_map:
            item_map[player] = items[item_index]
            item_map[against] = items[item_index]
            item_index += 1
    items = [item_map[p] for p in players]
    
    return items


def rank_points_to_avg_rank(sum_points: float, current_week: int) -> float:
    return (1 - (sum_points/current_week))*10 + 1


def remaining_opponent_avg_rank(season: pd.DataFrame, schedule: pd.DataFrame, current_week: int) -> list:
    """
    """
    
    remaining_schedule = schedule.loc[schedule[WEEK_COL] > current_week, :]
    roar = []
    for p in season[PLAYER_COL].to_list():
        opponents = remaining_schedule.loc[remaining_schedule[PLAYER_COL] == p, AGAINST_COL].to_list()
        rank_points = [season.loc[season[PLAYER_COL] == opp, 'RankPoints'].iloc[0] for opp in opponents]
        avg_ranks = [rank_points_to_avg_rank(rp, current_week) for rp in rank_points]
        roar.append(round(sum(avg_ranks)/len(avg_ranks), 2))
        
    return roar

	
SCHEDULE_URL = '2PACX-1vS4BxaruR77zq40juWJSOIyTnXeM55dSFpUo1FKAS9MH2N5dX4B93eaTUafyiBVeg/pub?gid=1590080431'
POINTS_URL = '2PACX-1vS4BxaruR77zq40juWJSOIyTnXeM55dSFpUo1FKAS9MH2N5dX4B93eaTUafyiBVeg/pub?gid=769575652'
WEEK_COL = 'Week'
PLAYER_COL = 'Player'
AGAINST_COL = 'Against'
POINTS_COL = 'Points'
COLORS = ["#EC7063", "#AF7AC5", "#5DADE2", "#48C9B0", "#F9E79F", "#E59866",
          "#F06292", "#58D68D", "#AED6F1", "#F8BBD0"]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

schedule_wide, points_wide = read_data(SCHEDULE_URL, POINTS_URL)
# TODO: validation checks
schedule = pd.melt(schedule_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=AGAINST_COL)
points = supplement_points(points_wide, schedule, WEEK_COL, PLAYER_COL, AGAINST_COL, POINTS_COL)
points['RankPoints'] = points.groupby(WEEK_COL)[POINTS_COL].rank()/len(schedule[PLAYER_COL].unique())
points['ExpectedWin'] = expected_win(points, WEEK_COL, POINTS_COL)
season = calculate_season_stats(points, PLAYER_COL, POINTS_COL, AGAINST_COL)

PLAYERS = [col for col in schedule_wide.columns if col != WEEK_COL]
#players = season.sort_values(by='Place', ascending=True)[PLAYER_COL].to_list()
current_week = points.loc[:, WEEK_COL].max()
season['RemainOppAvgRank'] = remaining_opponent_avg_rank(season, schedule, current_week)

app.layout = html.Div([
    html.Br(),
    html.H5(WEEK_COL),
    dcc.Slider(
        id='week-slider',
        min=schedule_wide[WEEK_COL].min(),
        max=schedule_wide[WEEK_COL].max(),
        value=current_week,
        marks={str(wk): (str(wk) if wk != current_week else "Current") for wk in schedule_wide[WEEK_COL].unique()},
        step=None
#        updatemode='drag'  - not fast enough to update as it's dragged
        ),
    html.Br(),
    dcc.Graph(id='week-points'),
    dcc.Graph(id='season-dist-pts'),
    dcc.Graph(id='season-dist-vs'),
    dcc.Graph(id='season-dist-rank'),
    html.Br(),
    generate_dash_table(season),
    html.Br()
    ],
    style={'textAlign': 'center'})


@app.callback(
    Output('week-points', 'figure'),
    [Input('week-slider', 'value')]
)
def update_week_points_fig(week: int):
    week_schedule = schedule.loc[schedule[WEEK_COL] == week, :]
    if week > current_week:
        week_points = [1]*len(PLAYERS)
        week_players = PLAYERS.copy()
        week_won = [0]*len(PLAYERS)
#        return go.Figure([go.Bar(x=[], y=[])])
    else:
        week_points_df = points.loc[(points[WEEK_COL] == week), :]
        week_points_df = week_points_df.sort_values(by=POINTS_COL, ascending=False)
        week_points = week_points_df[POINTS_COL].to_list()
        week_players = week_points_df[PLAYER_COL].to_list()
        week_won = [int(won) for won in week_points_df['Won'].to_list()]
    week_colors = [COLORS[PLAYERS.index(wp)] for wp in week_players]
    week_texts = get_matchup_items(week_players, week_schedule,
                     ["<b>{}</b>".format(i+1) for i in range(int(len(week_players)/2))])
    
    week_points_fig = go.Figure([go.Bar(
        x=week_players,
        y=week_points,
        marker_color=week_colors,
        marker_line_width=[2*ww for ww in week_won],
        marker_line_color='black',
        text=week_texts,
        textfont={'size': 16},
        textposition='auto',
        hoverinfo="y")])
    week_points_fig.update_xaxes(tickfont={"size": 18})
    week_points_fig.update_yaxes(title_text=POINTS_COL,
                                 title_font={"size": 22}, tickfont={"size": 18})
    
    week_points_fig.update_layout(
        autosize=False, height=400,
        margin=go.layout.Margin(l=50, r=50, b=25, t=25, pad=4),
        title=dict(
            text='Numbers = matchup. Box outline = won.',
            xref='paper', yref='paper',
            x=0.99, y=0.8,
            xanchor='right', yanchor='bottom')
    )
    
    return week_points_fig


def update_season_dist_plot(week: int, y_col: str):
    temp_points = points.loc[points[WEEK_COL] <= week, :]
    temp_season = calculate_season_stats(temp_points, PLAYER_COL, POINTS_COL, AGAINST_COL)
    temp_players = temp_season.sort_values(by='Place', ascending=True)[PLAYER_COL].to_list()
    fig = go.Figure()
    for player in temp_players:
        player_points = temp_points.loc[temp_points[PLAYER_COL] == player, :]
        marker_colors = ['limegreen' if won else 'red' for won in player_points['Won'].to_list()]
        fig.add_trace(
            go.Violin(
                x=player_points.loc[:, PLAYER_COL],
                y=player_points.loc[:, y_col],
                fillcolor=COLORS[PLAYERS.index(player)],
                line_color='gray',
                name=player,
                legendgroup=player,
                box_visible=False,
                pointpos=0,
                meanline_visible=True,
                points='all')
            )
            
#        fig.add_trace(
#            go.Scatter(
#                x=player_points.loc[:, PLAYER_COL],
#                y=player_points.loc[:, y_col],
#                mode='markers',
#                marker=dict(
#                    color=marker_colors,
#                    line=dict(width=2,
#                              color='gray') # DarkSlateGrey
#                ),
#                legendgroup=player)
#            )
        
    fig.update_xaxes(tickfont={"size": 18})
    fig.update_yaxes(title_text=y_col,
                     title_font={"size": 22}, tickfont={"size": 18})
    fig.update_layout(
        autosize=False, height=400,
        margin=go.layout.Margin(l=50, r=50, b=25, t=25, pad=4)
    )
    
    return fig


@app.callback(
    Output('season-dist-pts', 'figure'),
    [Input('week-slider', 'value')]
)
def update_season_dist_pts_fig(week: int):
    return update_season_dist_plot(week, POINTS_COL)

@app.callback(
    Output('season-dist-vs', 'figure'),
    [Input('week-slider', 'value')]
)
def update_season_dist_vs_fig(week: int):
    return update_season_dist_plot(week, POINTS_COL+AGAINST_COL)

@app.callback(
    Output('season-dist-rank', 'figure'),
    [Input('week-slider', 'value')]
)
def update_season_dist_rank_fig(week: int):
    return update_season_dist_plot(week, 'RankPoints')


if __name__ == '__main__':
    app.run_server(debug=True)