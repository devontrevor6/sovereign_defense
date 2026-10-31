import socket
import threading
import time
import random
import os
from concurrent.futures import ThreadPoolExecutor

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 9999
CONCURRENCY = 16
TOTAL_REQUESTS = 50

print(f"[*] Launching Corrected Slow-Hold Attack Simulation")

success_count = 0
timeout_blocked_count = 0
error_count = 0
lock = threading.Lock()

def fire_slow_hold_probe(i):
    global success_count, timeout_blocked_count, error_count
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(4.0)
            s.connect((TARGET_HOST, TARGET_PORT))
            
            # Send partial headers, then sleep to hold the connection open (Slowloris style)
            s.send(b"GET /slow HTTP/1.1\r\n")
            time.sleep(2.0) # Hold longer than server's 1.5s timeout
            
            try:
                s.send(b"Host: local\r\n\r\n")
                resp = s.recv(512)
                with lock:
                    if b"408" in resp or b"Timeout" in resp:
                        timeout_blocked_count += 1
                    else:
                        success_count += 1
            except socket.timeout:
                with lock:
                    timeout_blocked_count += 1
            except:
                with lock:
                    error_count += 1
    except:
        with lock:
            error_count += 1

if __name__ == '__main__':
    os.system("fuser -k 9999/tcp 2>/dev/null")
    daemon_pid = os.spawnl(os.P_NOWAIT, "/usr/bin/python3", "python3", "native_ai_matrix.py")
    time.sleep(1)

    start = time.time()
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        list(executor.map(fire_slow_hold_probe, range(TOTAL_REQUESTS)))
    elapsed = time.time() - start

    os.system(f"kill {daemon_pid} 2>/dev/null")
    os.system("fuser -k 9999/tcp 2>/dev/null")

    print("\n" + "="*50)
    print("   CORRECTED SLOW-HOLD TEST RESULTS")
    print("="*50)
    print(f" Total Time Elapsed     : {elapsed:.2f} seconds")
    print(f" Handled / Passed       : {success_count}")
    print(f" Caught & Timed-Out     : {timeout_blocked_count}")
    print(f" Connection Errors      : {error_count}")
    print("="*50)
