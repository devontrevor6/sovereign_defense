import sqlite3
import os

DB_FILE = os.path.expanduser("~/sovereign_defense/native_ai_matrix.db")

def generate_report():
    if not os.path.exists(DB_FILE):
        print("[!] No audit database found yet.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM native_ai_audits")
    total_events = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM native_ai_audits WHERE action = 'ALLOWED'")
    allowed_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM native_ai_audits WHERE action = 'AI_DROPPED_AND_MITIGATED'")
    dropped_count = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(entropy_score) FROM native_ai_audits")
    avg_entropy = cursor.fetchone()[0] or 0.0

    print("\n" + "="*50)
    print("   SOVEREIGN MATRIX SECURITY AUDIT REPORT")
    print("="*50)
    print(f" Total Logged Events  : {total_events}")
    print(f" Clean Packets Allowed: {allowed_count}")
    print(f" Threats Neutralized  : {dropped_count}")
    print(f" Average Payload Entropy: {avg_entropy:.2f}")
    print("="*50)

    conn.close()

if __name__ == "__main__":
    generate_report()
