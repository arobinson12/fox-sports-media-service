import os
import pytest
from src.fox_sports_highlights import init_db, get_highlights_by_player, export_game_clip

TEST_DB = "/tmp/test_fox_sports.db"

@pytest.fixture(autouse=True)
def setup_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_query_highlights():
    highlights = get_highlights_by_player("NFL-2026-WK4-KC-BAL", "Patrick Mahomes", db_path=TEST_DB)
    assert len(highlights) == 1
    assert highlights[0][1] == "TOUCHDOWN"

def test_export_game_clip():
    success = export_game_clip("rtmp://fake.stream", "00:01:00", "5", "test_clip")
    assert success is True
