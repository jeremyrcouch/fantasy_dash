import pandas as pd

from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
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
    
    points = pd.melt(points_wide, id_vars=[id_col], var_name=player_col, value_name=points_col)
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
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))]
    )


def generate_dash_table(df, max_rows=float('Inf')):
     return dash_table.DataTable(
                id='season-stats-dash-table',
                columns=[{"name": col, "id": col} for col in df.columns], 
                data=df.to_dict('records'),
                style_table={'maxWidth': '600px'},
                style_cell={'textAlign': 'center'},
                style_as_list_view=True,
                style_header={'fontWeight': 'bold'},
                style_data_conditional = [{
                    'if': {
                        'column_id': 'ExpectedWins',
                        'filter_query': '{ExpectedWins} > {Wins}'
                    },
                    'backgroundColor': '#D1FAC1'
                },
                {
                    'if': {
                        'column_id': 'ExpectedWins',
                        'filter_query': '{ExpectedWins} < {Wins}'
                    },
                    'backgroundColor': '#FAC7C1'
                }],
                sort_action="native",
                sort_mode="multi"
            )

	
SCHEDULE_URL = '2PACX-1vS4BxaruR77zq40juWJSOIyTnXeM55dSFpUo1FKAS9MH2N5dX4B93eaTUafyiBVeg/pub?gid=1590080431'
POINTS_URL = '2PACX-1vS4BxaruR77zq40juWJSOIyTnXeM55dSFpUo1FKAS9MH2N5dX4B93eaTUafyiBVeg/pub?gid=769575652'
WEEK_COL = 'Week'
PLAYER_COL = 'Player'
AGAINST_COL = 'Against'
POINTS_COL = 'Points'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

schedule_wide, points_wide = read_data(SCHEDULE_URL, POINTS_URL)
schedule = pd.melt(schedule_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=AGAINST_COL)
points = supplement_points(points_wide, schedule, WEEK_COL, PLAYER_COL, AGAINST_COL, POINTS_COL)
points['RankPoints'] = points.groupby(WEEK_COL)[POINTS_COL].rank()/len(schedule[PLAYER_COL].unique())
points['ExpectedWin'] = expected_win(points, WEEK_COL, POINTS_COL)
season = calculate_season_stats(points, PLAYER_COL, POINTS_COL, AGAINST_COL)
players = season.sort_values(by='Place', ascending=True)[PLAYER_COL].to_list()


fig = go.Figure()
for player in players:
    fig.add_trace(go.Violin(x=points.loc[points[PLAYER_COL] == player, PLAYER_COL],
                            y=points.loc[points[PLAYER_COL] == player, POINTS_COL],
                            name=player,
                            box_visible=True,
                            meanline_visible=True,
                            points='all'))


app.layout = html.Div([
    dcc.Graph(
        id='player-points',
        figure=fig
    ),
    html.H4('Season Stats'),
    generate_dash_table(season)
])

if __name__ == '__main__':
    app.run_server(debug=True)