import pandas as pd
import pytest

from app.app import (
    rank_points_to_avg_rank,
    determine_points_against,
    remaining_opponent_avg_rank,
    collect_season_stats,
    get_matchup_items,
)
from app.app import WEEK_COL, PLAYER_COL, AGAINST_COL, POINTS_COL, RANK_COL, COL_JOIN

DATA_DIR = "./tests/data/"


@pytest.fixture
def schedule_wide():
    return pd.read_csv("{}{}".format(DATA_DIR, "schedule.csv"))


@pytest.fixture
def points_wide():
    return pd.read_csv("{}{}".format(DATA_DIR, "points.csv"))


@pytest.fixture
def points_final():
    return pd.read_csv("{}{}".format(DATA_DIR, "points_final.csv"))


@pytest.fixture
def season():
    return pd.read_csv("{}{}".format(DATA_DIR, "season.csv"))


def test_determine_points_against(points_wide, schedule_wide) -> float:
    # arrange
    points_data = pd.melt(
        points_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=POINTS_COL
    )
    schedule = pd.melt(
        schedule_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=AGAINST_COL
    )
    expected_cols = set([
        PLAYER_COL, WEEK_COL, AGAINST_COL,
        COL_JOIN.format(POINTS_COL, AGAINST_COL)
    ])

    # act
    points_against = determine_points_against(
        points_data, schedule, WEEK_COL, PLAYER_COL, AGAINST_COL, POINTS_COL
    )

    # assert
    assert isinstance(points_against, pd.DataFrame)
    assert set(points_against.columns) == expected_cols
    assert len(points_against) == len(points_data)


@pytest.mark.parametrize(
    "rank_points, current_week, expected_avg",
    [
        pytest.param(1, 1, 1, id="first"),
        pytest.param(0.1, 1, 10, id="last"),
        pytest.param(6, 10, 5, id="later-week"),
    ],
)
def test_rank_points_to_avg_rank(rank_points, current_week, expected_avg) -> float:
    # arrange

    # act
    avg_rank = rank_points_to_avg_rank(rank_points, current_week)

    # assert
    assert isinstance(avg_rank, float)
    assert avg_rank == expected_avg


@pytest.mark.parametrize(
    "current_week", [pytest.param(10, id="middle"),
                     pytest.param(14, id="last")]
)
def test_remaining_opponent_avg_rank(current_week, season, schedule_wide):
    # arrange
    schedule = pd.melt(
        schedule_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=AGAINST_COL
    )

    # act
    roar = remaining_opponent_avg_rank(
        season,
        schedule,
        current_week,
        WEEK_COL,
        PLAYER_COL,
        AGAINST_COL,
        POINTS_COL,
        RANK_COL,
    )

    # assert
    assert isinstance(roar, list)
    if current_week == schedule[WEEK_COL].max():
        assert all([r == 0 for r in roar])
    else:
        assert min(roar) > 0


def test_collect_season_stats(season, points_final, schedule_wide):
    # arrange
    schedule = pd.melt(
        schedule_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=AGAINST_COL
    )

    # act
    season_test = collect_season_stats(
        points_final,
        schedule,
        WEEK_COL,
        PLAYER_COL,
        AGAINST_COL,
        POINTS_COL,
        RANK_COL,
    )

    # assert
    assert list(season_test.columns) == list(season.columns)
    assert season_test["Place"].to_list() == sorted(season_test["Place"].to_list())


def test_get_matchup_items(points_final, schedule_wide):
    # arrange
    week = 10
    schedule = pd.melt(
        schedule_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=AGAINST_COL
    )
    week_schedule = schedule.loc[schedule[WEEK_COL] == week, :]
    week_players = [col for col in schedule_wide.columns if col != WEEK_COL]
    items = ["{}".format(i + 1) for i in range(int(len(week_players)/2))]
    expected_items = ["1", "1", "2", "2", "3", "4", "3", "5", "5", "4"]

    # act
    matchup_items = get_matchup_items(
        week_players, week_schedule, items, PLAYER_COL, AGAINST_COL
    )

    # assert
    assert isinstance(matchup_items, list)
    assert matchup_items == expected_items
