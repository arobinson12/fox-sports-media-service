"""
Fox Sports Broadcast & Digital Media - Automated Highlight Processing Service
Handles live clipping of broadcast feeds for NFL, MLB, and FIFA game moments.
Includes interactive Web Dashboard & CLI runner.
"""

import os
import sys
import shutil
import sqlite3
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Tuple

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
    query = f"SELECT id, play_type, duration_sec, clip_path FROM game_highlights WHERE game_id = '{game_id}' AND player_name = '{player_name}'"
    print(f"[Fox Sports DB Query] Executing: {query}")
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def batch_export_clips(manifest: List[dict]):
    """Fox Sports Automation: Batch export live replay clips for social distribution."""
    results = []
    for item in manifest:
        ok = export_game_clip(item["stream"], item["start"], item["duration"], item["name"])
        results.append(ok)
    return results

class FoxSportsWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        results = []
        searched_player = params.get("player", [""])[0]
        if searched_player:
            results = get_highlights_by_player("NFL-2026-WK4-KC-BAL", searched_player)

        export_msg = ""
        if "output_name" in params:
            out_name = params.get("output_name", ["clip1"])[0]
            ok = export_game_clip("rtmp://live.foxsports.com/feed/live", "00:10:00", "15", out_name)
            export_msg = f"Clip exported: /tmp/highlights/{out_name}.mp4 (Success: {ok})"

        conn = sqlite3.connect(DEFAULT_DB_PATH)
        all_clips = conn.cursor().execute("SELECT game_id, player_name, play_type, duration_sec, clip_path FROM game_highlights").fetchall()
        conn.close()

        html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Fox Sports Highlight Service - Live Demo</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b162c; color: #fff; margin: 0; padding: 24px; }}
    .container {{ max-width: 900px; margin: 0 auto; background: #162447; border-radius: 12px; padding: 28px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
    .logo {{ color: #ffbe0b; font-size: 28px; font-weight: 800; letter-spacing: 1px; }}
    .subtitle {{ color: #8d99ae; font-size: 14px; margin-bottom: 24px; }}
    .card {{ background: #1f305e; border-radius: 8px; padding: 18px; margin-bottom: 20px; }}
    h2 {{ font-size: 18px; margin-top: 0; color: #ffbe0b; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
    th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #2a3d66; font-size: 14px; }}
    th {{ background: #121c38; color: #8d99ae; text-transform: uppercase; font-size: 11px; }}
    input[type=text] {{ padding: 10px 14px; border-radius: 6px; border: 1px solid #3a506b; background: #0b162c; color: #fff; width: 60%; font-size: 14px; }}
    button {{ padding: 10px 18px; border-radius: 6px; border: none; background: #ffbe0b; color: #0b162c; font-weight: bold; cursor: pointer; }}
    button:hover {{ background: #ffd166; }}
    .badge {{ background: #06d6a0; color: #0b162c; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
    .msg {{ margin-top: 10px; color: #06d6a0; font-family: monospace; font-size: 13px; }}
    .vuln-note {{ background: rgba(239, 71, 111, 0.15); border-left: 4px solid #ef476f; padding: 10px 14px; font-size: 13px; color: #ffccd5; margin-top: 10px; border-radius: 0 6px 6px 0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">FOX SPORTS <span style="font-weight: 300; color: #fff;">| Media Highlight Engine</span></div>
    <div class="subtitle">Live Broadcast Feed Processing & Metadata API &bull; Protected by Google CodeMender</div>

    <div class="card">
      <h2>1. Live Highlight Archive (Database)</h2>
      <table>
        <tr><th>Game ID</th><th>Player</th><th>Play</th><th>Duration</th><th>Path</th></tr>
        {"".join(f"<tr><td>{c[0]}</td><td><b>{c[1]}</b></td><td><span class='badge'>{c[2]}</span></td><td>{c[3]}s</td><td><code>{c[4]}</code></td></tr>" for c in all_clips)}
      </table>
    </div>

    <div class="card">
      <h2>2. Live Metadata Search</h2>
      <form method="GET" action="/">
        <input type="text" name="player" value="{searched_player}" placeholder="Search player (e.g. Patrick Mahomes or ' OR '1'='1)">
        <button type="submit">Search Metadata</button>
      </form>
      {"<div class='msg'>Found " + str(len(results)) + " matching highlight records!</div>" if searched_player else ""}
      <div class="vuln-note">
        <b>Demo SQL Injection:</b> Try typing <code>' OR '1'='1</code> into the search box to extract records across all games!
      </div>
    </div>

    <div class="card">
      <h2>3. Live Broadcast Clip Exporter</h2>
      <form method="GET" action="/">
        <input type="text" name="output_name" placeholder="Clip filename (e.g. mahomes_td_q4 or clip1; whoami)">
        <button type="submit">Export Clip via ffmpeg</button>
      </form>
      {"<div class='msg'>" + export_msg + "</div>" if export_msg else ""}
      <div class="vuln-note">
        <b>Demo Command Injection:</b> Try typing <code>clip1; whoami</code> to execute shell commands during video clipping!
      </div>
    </div>
  </div>
</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

def start_server(port: int = 8080):
    init_db()
    server = HTTPServer(("0.0.0.0", port), FoxSportsWebHandler)
    print(f"\n============================================================")
    print(f"🏈 Fox Sports Media Highlight Service running on:")
    print(f"👉 http://localhost:{port}")
    print(f"============================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Fox Sports server.")
        server.server_close()

if __name__ == "__main__":
    init_db()
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        start_server(8080)
    else:
        print("🏈 Fox Sports Highlights Service CLI Mode:")
        sample = get_highlights_by_player("NFL-2026-WK4-KC-BAL", "Patrick Mahomes")
        print(f"Sample query result: {sample}")
        export_game_clip("rtmp://live.foxsports.com/feed/nfl_superbowl", "00:14:22", "30", "touchdown_mahomes")
        print("\nTip: Run with --web to launch the browser UI: python3 src/fox_sports_highlights.py --web")
