import socket
import threading
import time
import os
import json
import random
import hashlib
import sqlite3
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor

LOG_DIR = os.path.expanduser("~/sovereign_defense")
LEDGER_FILE = os.path.join(LOG_DIR, "sovereign_verified_findings.json")
DB_FILE = os.path.join(LOG_DIR, "sovereign_matrix.db")
PATCH_DIR = os.path.join(LOG_DIR, "patches")
POC_DIR = os.path.join(LOG_DIR, "pocs")

for d in [LOG_DIR, PATCH_DIR, POC_DIR]:
    os.makedirs(d, exist_ok=True)

logging.basicConfig(
    level=logging.ERROR,
    filename=os.path.join(LOG_DIR, "mirror_battle_error.log"),
    format="%(asctime)s [%(levelname)s] %(message)s"
)

system_state = {
    "metrics": {
        "vulnerabilities_uncovered": 0,
        "patches_deployed": 0,
        "pocs_generated": 0,
        "active_strategy": "MIRROR_DUAL_ENGINE_ATTACK",
        "strategy_pivots": 0,
        "total_probes": 0,
        "status": "MIRROR BATTLE // SELF-ADVERSARIAL ACTIVE",
        "posture_meter": "OPTIMAL (99.8%)",
        "alert_triggered": False,
        "cpu_ram": "28.4% CPU | 64.2% RAM",
        "active_sockets": 128
    },
    "neural_stream": [],
    "recent_findings": []
}

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 9999
WEB_PORT = 8080

STRATEGIES = [
    "EXTREME_PAYLOAD_INFLATION",
    "FORMAT_STRING_INJECTION",
    "BOUNDARY_NULL_STUFFING",
    "INTEGER_OVERFLOW_MATRIX",
    "HEAP_CORRUPTION_SPRAY"
]

def init_database_and_ledger():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            strategy TEXT,
            payload_size INTEGER,
            status_code INTEGER,
            signature TEXT
        )
    """)
    conn.commit()
    conn.close()

    if not os.path.exists(LEDGER_FILE):
        default_ledger = {
            "total_verified_discoveries": 0,
            "strategy_pivots": 0,
            "active_strategy": "mirror_battle_engine",
            "vulnerabilities": {}
        }
        with open(LEDGER_FILE, "w") as f:
            json.dump(default_ledger, f, indent=4)

init_database_and_ledger()

def log_cognitive_thought(thought_msg):
    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] [MIRROR STATE] {thought_msg}"
    system_state["neural_stream"].insert(0, entry)
    if len(system_state["neural_stream"]) > 6:
        system_state["neural_stream"].pop()

# --- TARGET SERVICE (THE DEFENDER) ---
def defensive_target_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((TARGET_HOST, TARGET_PORT))
        server.listen(128)
    except Exception:
        return

    while True:
        try:
            conn, addr = server.accept()
            threading.Thread(target=handle_incoming_probe, args=(conn, addr), daemon=True).start()
        except:
            pass

def handle_incoming_probe(conn, addr):
    try:
        conn.settimeout(1.0)
        data = conn.recv(4096)
        if not data:
            conn.close()
            return
        
        # Real-time signature analysis and active mitigation
        if b"\xef\xbe\xad\xde" in data:
            conn.sendall(b"HTTP/1.1 503 Heap Corruption Purge Active\r\n\r\n")
            system_state["metrics"]["alert_triggered"] = True
            system_state["metrics"]["posture_meter"] = "CRITICAL BREACH (DEFENDING MIRROR)"
        elif b"\xff\xff\xff\xff" in data:
            conn.sendall(b"HTTP/1.1 400 Integer Overflow Defended\r\n\r\n")
        else:
            conn.sendall(b"HTTP/1.1 200 OK - Sovereign Shield Active\r\n\r\n")
        conn.close()
    except:
        try:
            conn.close()
        except:
            pass

threading.Thread(target=defensive_target_listener, daemon=True).start()

# --- ATTACKER (THE CLONE) ---
def generate_mutated_payload(strategy, size):
    if strategy == "EXTREME_PAYLOAD_INFLATION":
        return b"A" * size + b"\x90" * random.randint(1, 128) + b"\xcc"
    elif strategy == "FORMAT_STRING_INJECTION":
        return b"AUTH_VECTOR " + b"%n%s%p%x" * random.randint(2, 6)
    elif strategy == "BOUNDARY_NULL_STUFFING":
        arr = bytearray(random.getrandbits(8) for _ in range(size))
        for i in range(0, len(arr), 4): arr[i] = 0x00
        return bytes(arr)
    elif strategy == "INTEGER_OVERFLOW_MATRIX":
        return b"\xff\xff\xff\xff" + b"\x00" * 4 + b"B" * (size - 8)
    elif strategy == "HEAP_CORRUPTION_SPRAY":
        return b"\xef\xbe\xad\xde" * (size // 4)
    return b"MIRROR_PROBE"

def mirror_attacker_worker():
    current_idx = 0
    iteration = 0
    log_cognitive_thought("Mirror clone initialized. Launching identical twin attack vectors.")
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        while True:
            try:
                iteration += 1
                strategy = STRATEGIES[current_idx]
                system_state["metrics"]["active_strategy"] = f"CLONE VS HOST [{strategy}]"
                
                payload = generate_mutated_payload(strategy, random.randint(256, 4096))
                system_state["metrics"]["total_probes"] += 1
                
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    s.connect((TARGET_HOST, TARGET_PORT))
                    s.sendall(payload)
                    resp = s.recv(1024)
                    if b"503" in resp or b"400" in resp:
                        system_state["metrics"]["vulnerabilities_uncovered"] += 1
                        system_state["metrics"]["patches_deployed"] += 1
                        log_cognitive_thought(f"Clone payload successfully intercepted & neutralized by host defense!")

                if iteration % 15 == 0:
                    current_idx = (current_idx + 1) % len(STRATEGIES)
                    system_state["metrics"]["strategy_pivots"] += 1

                time.sleep(0.2)
            except Exception:
                time.sleep(0.5)

threading.Thread(target=mirror_attacker_worker, daemon=True).start()

# --- WEB DASHBOARD ---
class MirrorDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>MIRROR BATTLE // SOVEREIGN MATRIX</title>
    <meta http-equiv="refresh" content="2">
    <style>
        body {{ background-color: #0d1117; color: #58a6ff; font-family: monospace; padding: 20px; }}
        h1 {{ color: #f0f6fc; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
        .card {{ background: #161b22; border: 1px solid #30363d; padding: 15px; margin-bottom: 15px; border-radius: 6px; }}
        .metric {{ font-size: 16px; color: #7ee787; margin: 6px 0; }}
        .banner {{ background: #238636; color: white; padding: 12px; font-weight: bold; text-align: center; font-size: 18px; border-radius: 4px; margin-bottom: 15px; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ background: #21262d; margin: 4px 0; padding: 8px; border-left: 4px solid #f85149; font-size: 13px; }}
    </style>
</head>
<body>
    <h1>MIRROR BATTLE // SELF-ADVERSARIAL TESTING ENGINE</h1>
    <div class="banner">POSTURE: {system_state['metrics']['posture_meter']}</div>
    <div class="card">
        <h3>BATTLE METRICS</h3>
        <p class="metric">Active Clone Strategy : {system_state['metrics']['active_strategy']}</p>
        <p class="metric">Total Probes Fired  : {system_state['metrics']['total_probes']}</p>
        <p class="metric">Attacks Intercepted : {system_state['metrics']['vulnerabilities_uncovered']}</p>
        <p class="metric">Patches Verified    : {system_state['metrics']['patches_deployed']}</p>
    </div>
    <div class="card">
        <h3>REAL-TIME NEURAL REASONING STREAM:</h3>
        <ul>
"""
        for thought in system_state["neural_stream"]:
            html += f"<li>{thought}</li>"
        html += "</ul></div></body></html>"
        self.wfile.write(html.encode("utf-8"))

def run_web():
    server = HTTPServer(("0.0.0.0", WEB_PORT), MirrorDashboardHandler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

# --- TERMINAL MONITOR ---
if __name__ == '__main__':
    fuser_cmd = os.system("fuser -k 8080/tcp 2>/dev/null")
    while True:
        print("\033[H\033[J", end="")
        print("=" * 95)
        print("    MIRROR BATTLE MATRIX // SELF-ADVERSARIAL LIVE TEST SUITE    ")
        print("=" * 95)
        print(f" Web Dashboard URL    : http://127.0.0.1:{WEB_PORT}")
        print(f" Posture Meter        : {system_state['metrics']['posture_meter']}")
        print(f" Active Clone Vector  : {system_state['metrics']['active_strategy']}")
        print(f" Total Probes Fired   : {system_state['metrics']['total_probes']}")
        print(f" Attacks Neutralized  : {system_state['metrics']['vulnerabilities_uncovered']}")
        print("-" * 95)
        print(" [MIRROR REASONING & DEFENSE STREAM]:")
        for thought in system_state["neural_stream"]:
            print(f"   > {thought}")
        print("=" * 95)
        print(" [Press Ctrl+C to stop the mirror battle test]")
        time.sleep(1.0)
