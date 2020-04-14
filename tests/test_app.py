import pandas as pd
import pytest

from app.app import rank_points_to_avg_rank, determine_points_against
from app.app import WEEK_COL, PLAYER_COL, AGAINST_COL, POINTS_COL, RANK_COL, COL_JOIN


DATA_DIR = './tests/data/'


@pytest.fixture
def schedule_wide():
    return pd.read_csv('{}{}'.format(DATA_DIR, 'schedule.csv'))


@pytest.fixture
def points_wide():
    return pd.read_csv('{}{}'.format(DATA_DIR, 'points.csv'))


def test_determine_points_against(points_wide, schedule_wide) -> float:
    # arrange
    points_data = pd.melt(
        points_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=POINTS_COL
    )
    schedule = pd.melt(
        schedule_wide, id_vars=[WEEK_COL], var_name=PLAYER_COL, value_name=AGAINST_COL
    )
    expected_cols = set([PLAYER_COL, WEEK_COL, AGAINST_COL,
                         COL_JOIN.format(POINTS_COL, AGAINST_COL)])

    # act
    points_against = determine_points_against(points_data, schedule, WEEK_COL,
        PLAYER_COL, AGAINST_COL, POINTS_COL)

    # assert
    assert isinstance(points_against, pd.DataFrame)
    assert set(points_against.columns) == expected_cols
    assert len(points_against) == len(points_data)


@pytest.mark.parametrize('rank_points, current_week, expected_avg',
    [pytest.param(1, 1, 1, id='first'),
     pytest.param(0.1, 1, 10, id='last'),
     pytest.param(6, 10, 5, id='later-week')])
def test_rank_points_to_avg_rank(rank_points, current_week, expected_avg) -> float:
    # arrange

    # act
    avg_rank = rank_points_to_avg_rank(rank_points, current_week)

    # assert
    assert isinstance(avg_rank, float)
    assert avg_rank == expected_avg

