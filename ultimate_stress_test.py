import socket
import threading
import time
import random
import os
from concurrent.futures import ThreadPoolExecutor

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 9999
CONCURRENCY = 32
TOTAL_REQUESTS = 1000

print(f"[*] Launching Paced Stress Test: {CONCURRENCY} threads, {TOTAL_REQUESTS} requests")

success_count = 0
dropped_count = 0
error_count = 0
lock = threading.Lock()

def fire_probe(i):
    global success_count, dropped_count, error_count
    payloads = [
        b"A" * 1024,
        b"\xff\xff\xff\xff" * 256,
        b"NORMAL_USER_REQUEST_OK",
        b"\xef\xbe\xad\xde" * 512,
        b"GET /index.html HTTP/1.1\r\nHost: local\r\n\r\n"
    ]
    payload = random.choice(payloads)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            s.connect((TARGET_HOST, TARGET_PORT))
            s.sendall(payload)
            resp = s.recv(512)
            with lock:
                if b"403" in resp:
                    dropped_count += 1
                else:
                    success_count += 1
    except Exception as e:
        with lock:
            error_count += 1

if __name__ == '__main__':
    # 1. Clean port and start daemon via python
    os.system("fuser -k 9999/tcp 2>/dev/null")
    daemon_pid = os.spawnl(os.P_NOWAIT, "/usr/bin/python3", "python3", "native_ai_matrix.py")
    time.sleep(1)

    start = time.time()
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        list(executor.map(fire_probe, range(TOTAL_REQUESTS)))
    elapsed = time.time() - start

    # Cleanup background server
    os.system(f"kill {daemon_pid} 2>/dev/null")
    os.system("fuser -k 9999/tcp 2>/dev/null")

    print("\n" + "="*50)
    print("   FINAL STRESSED VERIFICATION RESULTS")
    print("="*50)
    print(f" Total Time Elapsed : {elapsed:.2f} seconds")
    print(f" Clean Packets Allowed: {success_count}")
    print(f" AI Blocked / Dropped : {dropped_count}")
    print(f" Connection Errors  : {error_count}")
    print("="*50)
