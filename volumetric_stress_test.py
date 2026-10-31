import socket
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 9999
CONCURRENCY = 256
TOTAL_REQUESTS = 5000

print(f"[*] Initializing High-Volume Stress Test against {TARGET_HOST}:{TARGET_PORT}")
print(f"[*] Concurrency Level: {CONCURRENCY} threads | Target Requests: {TOTAL_REQUESTS}")

success_count = 0
dropped_count = 0
error_count = 0
lock = threading.Lock()

def fire_stress_probe(worker_id):
    global success_count, dropped_count, error_count
    payload_types = [
        b"A" * 8192,
        b"\xff\xff\xff\xff" * 512,
        b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n" * 10,
        b"\xef\xbe\xad\xde" * 1024
    ]
    payload = random.choice(payload_types)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((TARGET_HOST, TARGET_PORT))
            s.sendall(payload)
            resp = s.recv(1024)
            with lock:
                if b"503" in resp or b"403" in resp or b"Forbidden" in resp:
                    dropped_count += 1
                else:
                    success_count += 1
    except socket.timeout:
        with lock:
            dropped_count += 1
    except ConnectionRefusedError:
        with lock:
            error_count += 1
    except Exception:
        with lock:
            error_count += 1

def run_load_test():
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(fire_stress_probe, i) for i in range(TOTAL_REQUESTS)]
        for f in futures:
            try:
                f.result(timeout=1.0)
            except:
                pass
    elapsed = time.time() - start_time
    print("\n" + "="*50)
    print("      HIGH-VOLUME STRESS TEST RESULTS")
    print("="*50)
    print(f" Total Time Elapsed : {elapsed:.2f} seconds")
    print(f" Successful Packets : {success_count}")
    print(f" Mitigated / Dropped: {dropped_count}")
    print(f" Connection Errors  : {error_count}")
    print("="*50)

if __name__ == "__main__":
    run_load_test()
