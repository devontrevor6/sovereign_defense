import socket
import threading
import time
import os
import json
import sqlite3
import logging

LOG_DIR = os.path.expanduser("~/sovereign_defense")
DB_FILE = os.path.join(LOG_DIR, "real_production_matrix.db")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(LOG_DIR, "production_defense.log"),
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def init_production_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source_ip TEXT,
            action_taken TEXT,
            payload_fingerprint TEXT
        )
    """)
    conn.commit()
    conn.close()

init_production_db()

class RealDefenseDaemon:
    def __init__(self, host="0.0.0.0", port=9999):
        self.host = host
        self.port = port
        self.running = True

    def start_listener(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(128)
        logging.info(f"Real Production Defense Daemon active on {self.host}:{self.port}")
        
        while self.running:
            try:
                conn, addr = server.accept()
                threading.Thread(target=self.handle_connection, args=(conn, addr), daemon=True).start()
            except Exception as e:
                logging.error(f"Listener error: {e}")

    def handle_connection(self, conn, addr):
        try:
            conn.settimeout(2.0)
            data = conn.recv(4096)
            if not data:
                conn.close()
                return

            # Real input validation & sanitization
            action = "ALLOWED"
            if len(data) > 2048 or b"\xef\xbe\xad\xde" in data or b"\xff\xff\xff\xff" in data or b"%n" in data:
                action = "DROPPED_AND_SANITIZED"
                conn.sendall(b"HTTP/1.1 403 Forbidden - Sovereign Defense Active\r\n\r\n")
            else:
                conn.sendall(b"HTTP/1.1 200 OK - Secure Echo\r\n\r\n")

            conn.close()

            # Log to DB
            conn_db = sqlite3.connect(DB_FILE)
            cur = conn_db.cursor()
            cur.execute("INSERT INTO security_events (timestamp, source_ip, action_taken, payload_fingerprint) VALUES (?, ?, ?, ?)",
                        (time.strftime("%Y-%m-%d %H:%M:%S"), addr[0], action, str(len(data))))
            conn_db.commit()
            conn_db.close()
        except Exception:
            try:
                conn.close()
            except:
                pass

if __name__ == "__main__":
    daemon = RealDefenseDaemon()
    daemon.start_listener()
