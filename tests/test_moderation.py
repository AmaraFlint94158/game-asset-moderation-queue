from src.game_asset_moderator import review_asset


def test_high_score_stays_out_of_the_catalog():
    result = review_asset("player_7", "asset_9", 0.82)
    assert result.decision == "hold_for_review"


def test_low_score_can_be_published():
    result = review_asset("player_7", "asset_10", 0.12)
    assert result.decision == "publish"

