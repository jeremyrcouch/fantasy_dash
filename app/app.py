from typing import List

import pandas as pd
import plotly.graph_objs as go

from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output

GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/e/{}&single=true&output=csv"
SCHEDULE_URL = "2PACX-1vS4BxaruR77zq40juWJSOIyTnXeM55dSFpUo1FKAS9MH2N5dX4B93eaTUafyiBVeg/pub?gid=1184397163"
POINTS_URL = "2PACX-1vS4BxaruR77zq40juWJSOIyTnXeM55dSFpUo1FKAS9MH2N5dX4B93eaTUafyiBVeg/pub?gid=2069019650"

WEEK_COL = "Week"
PLAYER_COL = "Player"
AGAINST_COL = "Against"
POINTS_COL = "Points"
RANK_COL = "Rank"
COL_JOIN = "{} {}"
CLOSE_MATCH_DIFF = 10
COLORS = [
    "#EC7063",
    "#AF7AC5",
    "#5DADE2",
    "#48C9B0",
    "#F9E79F",
    "#E59866",
    "#F06292",
    "#58D68D",
    "#AED6F1",
    "#F8BBD0",
]


def determine_points_against(
    points_data: pd.DataFrame,
    schedule: pd.DataFrame,
    id_col: str,
    player_col: str,
    against_col: str,
    points_col: str,
) -> pd.DataFrame:
    """Determine points against.
    
    Args:
        points_wide: DataFrame, weekly points data
        schedule: DataFrame, schedule information
        id_col: str, name of identifier column
        player_col: str, player column name
        against_col: str, vs column name
        points_col: str, points column name
        
    Returns:
        points_against: DataFrame, weekly points against
    """

    against = pd.merge(points_data, schedule, on=[id_col, player_col], how="left")
    against = against.drop([points_col], axis=1)
    against_points = points_data.loc[:, [id_col, player_col, points_col]]
    against_points = against_points.rename(
        columns={
            player_col: against_col,
            points_col: COL_JOIN.format(points_col, against_col),
        }
    )
    points_against = pd.merge(
        against, against_points, on=[id_col, against_col], how="left"
    )

    return points_against


def rank_scoring(rank: float, num_players: int) -> float:
    """Convert rank into a score (points).

    Args:
        rank: float, rank value
        num_players: int, number of players in league
    
    Returns:
        _: float, score value (points)
    """

    return rank/num_players


def rank_points_to_avg_rank(sum_points: float, current_week: int) -> float:
    """Average rank (1 highest, 10 lowest) based on total rank points at current week.
    Assumes 10 players, 1st = 1, 10th = 0.1.

    Args:
        sum_points: float, sum of rank points through current week
        current_week: int, current week number
    
    Returns:
        _: float, average rank
    """

    return (1 - (sum_points/current_week))*10 + 1


def remaining_opponent_avg_rank(
    season: pd.DataFrame,
    schedule: pd.DataFrame,
    current_week: int,
    id_col: str,
    player_col: str,
    against_col: str,
    points_col: str,
    rank_col: str,
) -> List[float]:
    """Average rank of remaining opponents in schedule for each player.

    Args:
        season: DataFrame, season stats
        schedule: DataFrame, matchup schedule
        current_week: int, current week number
        id_col: str, name of identifier column
        player_col: str, player column name
        against_col: str, vs column name
        points_col: str, points column name
        rank_col: str, rank column name

    Returns:
        roar: list of float, average ranks of remaining opponents
    """

    remaining_schedule = schedule.loc[schedule[id_col] > current_week, :]
    roar = []
    for p in season[player_col].to_list():
        if len(remaining_schedule) > 0:
            opponents = remaining_schedule.loc[remaining_schedule[player_col] ==
                                               p, against_col]
            rank_points = []
            for opp in opponents.to_list():
                rank_points.append(
                    season.loc[season[player_col] == opp,
                               COL_JOIN.format(rank_col, points_col)].iloc[0]
                )
            # only works for 10 players, 0.1 to 1 rank pts per week
            # if use this version, change column to "Remain Opp Avg Rank"
            # avg_ranks = [
            #     rank_points_to_avg_rank(rp, current_week) for rp in rank_points
            # ]
            avg_ranks = [rp/current_week for rp in rank_points]
            roar.append(round(sum(avg_ranks)/len(avg_ranks), 2))
        else:
            roar.append(0)

    return roar


# NOTE: grouped all this functionality together to make updating season stats..
#       simple during app callbacks
def collect_season_stats(
    points: pd.DataFrame,
    schedule: pd.DataFrame,
    id_col: str,
    player_col: str,
    against_col: str,
    points_col: str,
    rank_col: str,
) -> pd.DataFrame:
    """Collect season statistics given points data.

    Args:
        points: DataFrame, weekly points data
        schedule: DataFrame, schedule info for specific week
        id_col: str, name of identifier column
        player_col: str, player column name
        against_col: str, vs column name
        points_col: str, points column name
        rank_col: str, rank column name
    
    Returns:
        season: DataFrame, season stats
    """

    season = points.groupby(player_col).agg({
        points_col: "sum",
        COL_JOIN.format(points_col, against_col): "sum",
        "Won": "sum",
        COL_JOIN.format(rank_col, points_col): "sum",
        "Expected Win": "sum",
        "Close Win": "sum",
        "Close Loss": "sum",
    })
    season = season.rename(
        columns={
            "Won": "Wins",
            "Expected Win": "Expected Wins",
            "Close Win": "Close Wins",
            "Close Loss": "Close Losses",
        }
    )
    season = season.round({
        points_col: 2,
        COL_JOIN.format(points_col, against_col): 2,
        COL_JOIN.format(rank_col, points_col): 1,
    })
    season["Total Points"] = (
        season.loc[:, "Wins"] + season.loc[:, COL_JOIN.format(rank_col, points_col)]
    )
    season["Place"] = season.loc[:, "Total Points"].rank(ascending=False)
    season = season.sort_values(by="Place", ascending=True)

    season_col_order = [
        "Place",
        player_col,
        points_col,
        COL_JOIN.format(points_col, against_col),
        "Wins",
        COL_JOIN.format(rank_col, points_col),
        "Total Points",
        "Expected Wins",
        "Close Wins",
        "Close Losses",
    ]
    season = season.reset_index().loc[:, season_col_order]

    current_week = points.loc[:, id_col].max()
    season["Remain Opp Avg Rank Pts"] = remaining_opponent_avg_rank(
        season,
        schedule,
        current_week,
        id_col,
        player_col,
        against_col,
        points_col,
        rank_col,
    )

    return season


def get_matchup_items(
    players: List[str],
    schedule: pd.DataFrame,
    items: list,
    player_col: str,
    against_col: str,
) -> list:
    """Assign objects to matched up pairs of players for a given week.

    Args:
        players: list of str, players
        schedule: DataFrame, schedule info for specific week
        items: list, anything to assign to matched up players for the week
        player_col: str, 
        against_col: str,

    Returns:
        matchup_items: list, items corresponding to each player
    """

    item_map = {}
    item_index = 0
    for player in players:
        against = schedule.loc[schedule[player_col] == player, against_col].iloc[0]
        if player not in item_map:
            item_map[player] = items[item_index]
            item_map[against] = items[item_index]
            item_index += 1
    matchup_items = [item_map[p] for p in players]

    return matchup_items


def update_season_dist_plot(week: int, y_col: str):
    """Updates specified season distribution plot. 

    Args:
        week: int, current week
        y_col: str, name of column to plot

    Returns:
        distribution figure
    """

    temp_points = points.loc[points[WEEK_COL] <= week, :]
    temp_points[COL_JOIN.format(
        AGAINST_COL, RANK_COL
    )] = temp_points.groupby(AGAINST_COL)[COL_JOIN.format(POINTS_COL, AGAINST_COL)].rank()
    temp_season = collect_season_stats(
        temp_points, schedule, WEEK_COL, PLAYER_COL, AGAINST_COL, POINTS_COL, RANK_COL
    )
    temp_players = temp_season.sort_values(by="Place",
                                           ascending=True)[PLAYER_COL].to_list()
    fig = go.Figure()
    for player in temp_players:
        player_points = temp_points.loc[temp_points[PLAYER_COL] == player, :]
        fig.add_trace(
            go.Violin(
                x=player_points.loc[:, PLAYER_COL],
                y=player_points.loc[:, y_col],
                fillcolor=COLORS[PLAYERS.index(player)],
                line_color="gray",
                name=player,
                legendgroup=player,
                box_visible=False,
                pointpos=0,
                meanline_visible=True,
                points="all",
            )
        )
    fig.update_xaxes(tickfont={"size": 18})
    fig.update_yaxes(title_text=y_col, title_font={"size": 22}, tickfont={"size": 18})
    fig.update_layout(
        autosize=False,
        height=400,
        margin=go.layout.Margin(l=50, r=50, b=25, t=25, pad=4),
    )

    return fig


app = Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])
server = app.server

### Google Sheets ###
# schedule_wide = pd.read_csv(GOOGLE_SHEETS_URL.format(SCHEDULE_URL))
# points_wide = pd.read_csv(GOOGLE_SHEETS_URL.format(POINTS_URL)).dropna()

### Local Data ###
schedule_wide = pd.read_csv('./data/schedule.csv')
points_wide = pd.read_csv('./data/points.csv')

# TODO: validation checks

PLAYERS = [col for col in schedule_wide.columns if col != WEEK_COL]

schedule = pd.melt(
    schedule_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=AGAINST_COL
)
points_data = pd.melt(
    points_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=POINTS_COL
)
points_against = determine_points_against(
    points_data, schedule, WEEK_COL, PLAYER_COL, AGAINST_COL, POINTS_COL
)
points = pd.merge(points_data, points_against, how="left", on=[WEEK_COL, PLAYER_COL])

current_week = points.loc[:, WEEK_COL].max()

points["Won"] = (
    points.loc[:, POINTS_COL] > points.loc[:, COL_JOIN.format(POINTS_COL, AGAINST_COL)]
)
# TODO: how to handle ties?
# TODO: how does .rank() handle ties in points.. and how does this impact rank -> score
points[RANK_COL] = points.groupby(WEEK_COL)[POINTS_COL].rank()
points[COL_JOIN.format(AGAINST_COL, RANK_COL)] = \
    points.groupby(WEEK_COL)[COL_JOIN.format(POINTS_COL, AGAINST_COL)].rank()
points[COL_JOIN.format(RANK_COL, POINTS_COL)] = \
    rank_scoring(points.loc[:, RANK_COL], len(PLAYERS))
points[COL_JOIN.format(COL_JOIN.format(RANK_COL, POINTS_COL), AGAINST_COL)] = \
    rank_scoring(points.loc[:, COL_JOIN.format(AGAINST_COL, RANK_COL)], len(PLAYERS))

points["Close Match"] = (
    abs(
        points.loc[:, POINTS_COL] -
        points.loc[:, COL_JOIN.format(POINTS_COL, AGAINST_COL)]
    ) <= CLOSE_MATCH_DIFF
)
points["Close Loss"] = (~points.loc[:, "Won"]) & points.loc[:, "Close Match"]
points["Close Win"] = points.loc[:, "Won"] & points.loc[:, "Close Match"]

# TODO: generic stat function??
week_med = points.groupby(WEEK_COL)[POINTS_COL].median().reset_index()
week_med = week_med.rename(columns={POINTS_COL: "Weekly Median Points"})
points = pd.merge(points, week_med, on=WEEK_COL, how="left")
points["Expected Win"] = (
    points.loc[:, POINTS_COL] > points.loc[:, "Weekly Median Points"]
)

season = collect_season_stats(
    points, schedule, WEEK_COL, PLAYER_COL, AGAINST_COL, POINTS_COL, RANK_COL
)

app.layout = html.Div(
    [
        html.Br(),
        html.H5("Select {}".format(WEEK_COL)),
        dcc.Slider(
            id="week-slider",
            min=schedule_wide[WEEK_COL].min(),
            max=schedule_wide[WEEK_COL].max(),
            value=current_week,
            marks={
                str(wk): (str(wk) if wk != current_week else "Current")
                for wk in schedule_wide[WEEK_COL].unique()
            },
            step=None
            # updatemode='drag'  - not fast enough to update as it's dragged
        ),
        html.Br(),
        html.Br(),
        dcc.Graph(id="week-points"),
        html.Br(),
        html.Br(),
        html.H5("Select Stat to Visualize"),
        dcc.Dropdown(
            id="plot-selector",
            options=[{
                "label": lab,
                "value": col
            } for lab, col in zip(
                [
                    "Points",
                    COL_JOIN.format(POINTS_COL, AGAINST_COL),
                    COL_JOIN.format(RANK_COL, POINTS_COL),
                    COL_JOIN.format(COL_JOIN.format(RANK_COL, POINTS_COL), AGAINST_COL),
                    "Opponents Season Score Rank (1 = opponent's lowest score of season, etc.)",
                ],
                [
                    POINTS_COL,
                    COL_JOIN.format(POINTS_COL, AGAINST_COL),
                    COL_JOIN.format(RANK_COL, POINTS_COL),
                    COL_JOIN.format(COL_JOIN.format(RANK_COL, POINTS_COL), AGAINST_COL),
                    COL_JOIN.format(AGAINST_COL, RANK_COL),
                ],
            )],
            value=POINTS_COL,
            clearable=False,
        ),
        # html.H6(id="season-dist-title"),
        html.Br(),
        dcc.Markdown(id="season-dist-title"),
        dcc.Graph(id="season-dist-selected"),
        html.Br(),
        # html.H6(id="season-stats-table-title"),
        dcc.Markdown(id="season-stats-table-title"),
        dash_table.DataTable(
            id="season-stats-table",
            columns=[{
                "name": col,
                "id": col
            } for col in season.columns],
            # style_table={"maxWidth": "900px"},
            style_cell={"textAlign": "center"},
            style_as_list_view=True,
            style_header={"fontWeight": "bold"},
            sort_action="native",
            sort_mode="multi",
        ),
        html.Br(),
    ],
    style={"textAlign": "center", "tableAlign": "center",
           "marginLeft": 50, "marginRight": 50},
)


@app.callback(
    Output("season-stats-table-title", "children"),
    [Input("week-slider", "value")]
)
def form_season_stats_table_title(week: int) -> str:
    return """_Season Stats at End of Week {} (select week at top to change)_""".format(week)


@app.callback(
    Output("season-dist-title", "children"),
    [Input("week-slider", "value")]
)
def form_season_stats_table_title(week: int) -> str:
    return """_Stats at End of Week {} (select week at top to change)_""".format(week)


@app.callback(
    Output("week-points", "figure"),
    [Input("week-slider", "value")]
)
def update_week_points_fig(week: int):
    """Updates current week's points figure. 

    Args:
        week: int, current week

    Returns:
        figure
    """

    week_schedule = schedule.loc[schedule[WEEK_COL] == week, :]
    if week > current_week:
        week_points = [1]*len(PLAYERS)
        week_players = PLAYERS.copy()
        week_won = [0]*len(PLAYERS)
        # return go.Figure([go.Bar(x=[], y=[])])
    else:
        week_points_df = points.loc[(points[WEEK_COL] == week), :]
        week_points_df = week_points_df.sort_values(by=POINTS_COL, ascending=False)
        week_points = week_points_df[POINTS_COL].to_list()
        week_players = week_points_df[PLAYER_COL].to_list()
        week_won = [int(won) for won in week_points_df["Won"].to_list()]

    week_colors = [COLORS[PLAYERS.index(wp)] for wp in week_players]
    matchup_numbers = ["<b>{}</b>".format(i + 1) for i in range(int(len(week_players)/2))]
    week_texts = get_matchup_items(
        week_players, week_schedule, matchup_numbers, PLAYER_COL, AGAINST_COL
    )

    week_points_fig = go.Figure([
        go.Bar(
            x=week_players,
            y=week_points,
            marker_color=week_colors,
            marker_line_width=[2*ww for ww in week_won],
            marker_line_color="black",
            text=week_texts,
            textfont={"size": 16},
            textposition="auto",
            hoverinfo="y",
        )
    ])
    week_points_fig.update_xaxes(tickfont={"size": 18})
    week_points_fig.update_yaxes(
        title_text=POINTS_COL, title_font={"size": 22}, tickfont={"size": 18}
    )

    week_points_fig.update_layout(
        autosize=False,
        height=400,
        margin=go.layout.Margin(l=50, r=50, b=25, t=25, pad=4),
        title=dict(
            text="Numbers = matchup. Box outline = won.",
            xref="paper",
            yref="paper",
            x=0.99,
            y=0.8,
            xanchor="right",
            yanchor="bottom",
        ),
    )

    return week_points_fig


@app.callback(
    Output("season-dist-selected", "figure"),
    [Input("week-slider", "value"),
     Input("plot-selector", "value")],
)
def update_season_dist_pts_fig(week: int, col: str):
    """Callback wrapper around update_season_dist_plot."""
    return update_season_dist_plot(week, col)


@app.callback(
    Output("season-stats-table", "data"),
    [Input("week-slider", "value")]
)
def update_season_stats_table(week: int):
    """Updates season stats table up to current week.

    Args:
        week: int, current week

    Returns:
        figure
    """

    temp_points = points.loc[points[WEEK_COL] <= week, :]
    temp_points.loc[:, COL_JOIN.format(AGAINST_COL, RANK_COL)] = \
        temp_points.groupby(AGAINST_COL)[COL_JOIN.format(POINTS_COL, AGAINST_COL)].rank()
    temp_season = collect_season_stats(
        temp_points, schedule, WEEK_COL, PLAYER_COL, AGAINST_COL, POINTS_COL, RANK_COL
    )
    return temp_season.to_dict("records")


if __name__ == "__main__":

    app.run_server(debug=True)
