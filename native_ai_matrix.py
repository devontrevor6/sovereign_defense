import socket
import threading
import time
import os
import sqlite3
import math
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

LOG_DIR = os.path.expanduser("~/sovereign_defense")
DB_FILE = os.path.join(LOG_DIR, "native_ai_matrix.db")
os.makedirs(LOG_DIR, exist_ok=True)

ip_strikes = defaultdict(int)
blacklisted_ips = set()
state_lock = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS native_ai_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            client_ip TEXT,
            action TEXT,
            payload_size INTEGER,
            entropy_score REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def handle_connection(conn, addr):
    client_ip = addr[0]
    with state_lock:
        if client_ip in blacklisted_ips:
            try:
                conn.sendall(b"HTTP/1.1 429 Too Many Requests - IP Blacklisted\r\n\r\n")
                conn.close()
            except:
                pass
            return

    try:
        conn.settimeout(1.0)
        start_time = time.time()
        buffer = bytearray()
        while b"\r\n\r\n" not in buffer:
            if time.time() - start_time > 1.5:
                raise socket.timeout("Slow-rate timeout exceeded")
            chunk = conn.recv(1024)
            if not chunk:
                break
            buffer.extend(chunk)

        data = bytes(buffer)
        p_size = len(data)
        entropy = -sum((data.count(b) / p_size) * math.log2(data.count(b) / p_size) for b in set(data)) if p_size > 0 else 0.0

        action = "ALLOWED"
        if entropy > 4.5 or p_size > 3000 or b"\xef\xbe\xad\xde" in data:
            action = "AI_DROPPED_AND_MITIGATED"
            conn.sendall(b"HTTP/1.1 403 Forbidden - Shield Active\r\n\r\n")
            with state_lock:
                ip_strikes[client_ip] += 1
                if ip_strikes[client_ip] >= 3:
                    blacklisted_ips.add(client_ip)
        else:
            conn.sendall(b"HTTP/1.1 200 OK - Chromebook Secure Echo\r\n\r\n")

        conn.close()
        conn_db = sqlite3.connect(DB_FILE)
        cur = conn_db.cursor()
        cur.execute("INSERT INTO native_ai_audits (timestamp, client_ip, action, payload_size, entropy_score) VALUES (?, ?, ?, ?, ?)",
                    (time.strftime("%Y-%m-%d %H:%M:%S"), client_ip, action, p_size, entropy))
        conn_db.commit()
        conn_db.close()
    except:
        try: conn.close()
        except: pass

def native_ai_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 9999))
    server.listen(512)
    executor = ThreadPoolExecutor(max_workers=64)
    while True:
        try:
            conn, addr = server.accept()
            executor.submit(handle_connection, conn, addr)
        except:
            pass

if __name__ == '__main__':
    print("[*] Starting Chromebook Sovereign Matrix Daemon on Port 9999...")
    native_ai_listener()
