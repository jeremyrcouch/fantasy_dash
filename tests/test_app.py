from app.app import rank_points_to_avg_rank


def test_rank_points_to_avg_rank() -> float:
    # arrange
    sum_points = 100
    current_week = 5

    # act
    avg_rank = rank_points_to_avg_rank(sum_points, current_week)

    # assert
    assert isinstance(avg_rank, float)