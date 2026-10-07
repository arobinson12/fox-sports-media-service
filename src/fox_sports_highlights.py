"""
Fox Sports Broadcast & Digital Media - Automated Highlight Processing Service
Handles live clipping of broadcast feeds for NFL, MLB, and FIFA game moments.
"""

import os
import shutil
import sqlite3
from typing import List, Tuple, Optional

DEFAULT_DB_PATH = "fox_sports_metadata.db"

def init_db(db_path: str = DEFAULT_DB_PATH):
    """Initializes SQLite schema and seeds baseline highlight data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_highlights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            play_type TEXT NOT NULL,
            duration_sec INTEGER NOT NULL,
            clip_path TEXT NOT NULL
        )
    """)
    # Seed initial highlight clips if empty
    cursor.execute("SELECT count(*) FROM game_highlights")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO game_highlights (game_id, player_name, play_type, duration_sec, clip_path)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("NFL-2026-WK4-KC-BAL", "Patrick Mahomes", "TOUCHDOWN", 18, "/storage/clips/mahomes_td_01.mp4"),
            ("NFL-2026-WK4-KC-BAL", "Travis Kelce", "RECEPTION", 12, "/storage/clips/kelce_rec_02.mp4"),
            ("MLB-2026-ALCS-G1-NYY-HOU", "Aaron Judge", "HOME_RUN", 24, "/storage/clips/judge_hr_01.mp4")
        ])
    conn.commit()
    conn.close()

def export_game_clip(stream_source: str, start_time: str, duration: str, output_name: str) -> bool:
    """
    Extracts high-resolution highlight clips from live Fox Sports broadcast streams.
    
    SECURITY VULNERABILITY (CWE-78):
    Unsanitized parameters passed directly to shell command.
    Attacker can inject arbitrary commands via stream_source or output_name.
    """
    os.makedirs("/tmp/highlights", exist_ok=True)
    # Vulnerable shell concatenation
    ffmpeg_bin = shutil.which("ffmpeg") or "echo [simulated-ffmpeg]"
    ffmpeg_cmd = f"{ffmpeg_bin} -y -ss {start_time} -i {stream_source} -t {duration} -c copy /tmp/highlights/{output_name}.mp4"
    print(f"[Fox Sports Media Engine] Exporting clip: {ffmpeg_cmd}")
    exit_code = os.system(ffmpeg_cmd)
    return exit_code == 0

def get_highlights_by_player(game_id: str, player_name: str, db_path: str = DEFAULT_DB_PATH) -> List[Tuple]:
    """
    Queries highlight metadata for Fox Sports interactive app and on-air graphics.
    
    SECURITY VULNERABILITY (CWE-89):
    Raw string formatting concatenates untrusted player_name directly into SQL string.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Vulnerable raw string interpolation
    query = f"SELECT id, play_type, duration_sec, clip_path FROM game_highlights WHERE game_id = '{game_id}' AND player_name = '{player_name}'"
    print(f"[Fox Sports DB Query] Executing: {query}")
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    init_db()
    print("Fox Sports Highlights Service initialized successfully.")
    sample = get_highlights_by_player("NFL-2026-WK4-KC-BAL", "Patrick Mahomes")
    print(f"Sample query result: {sample}")
    export_game_clip("rtmp://live.foxsports.com/feed/nfl_superbowl", "00:14:22", "30", "touchdown_mahomes")
