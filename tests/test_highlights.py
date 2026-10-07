import os
import unittest
from src.fox_sports_highlights import init_db, get_highlights_by_player, export_game_clip

TEST_DB = "/tmp/test_fox_sports.db"

class TestFoxSportsHighlights(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_db(TEST_DB)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_query_highlights(self):
        highlights = get_highlights_by_player("NFL-2026-WK4-KC-BAL", "Patrick Mahomes", db_path=TEST_DB)
        self.assertEqual(len(highlights), 1)
        self.assertEqual(highlights[0][1], "TOUCHDOWN")

    def test_export_game_clip(self):
        success = export_game_clip("rtmp://fake.stream", "00:01:00", "5", "test_clip")
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
