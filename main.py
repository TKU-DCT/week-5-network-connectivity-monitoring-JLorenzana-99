import psutil
from datetime import datetime
import csv
import os
import time
import subprocess


def get_system_info():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    ping_status, ping_ms = ping_host("8.8.8.8")
    return [now, cpu, memory, disk, ping_status, ping_ms]


def ping_host(host):
    """
    Check connectivity using curl as alternative to ping.
    Tests connection to google.com (more reliable than raw IP in Codespaces).
    """
    try:
        # Use curl with timeout to check connectivity
        # -s: silent, -o /dev/null: discard output, -w: write out time
        # --connect-timeout: connection timeout in seconds
        # Note: Using google.com instead of IP address for better compatibility
        command = [
            "curl", 
            "-s", 
            "-o", "/dev/null",
            "-w", "%{time_total}",
            "--connect-timeout", "3",
            "--max-time", "5",
            "http://www.google.com"
        ]
        
        # Use run() instead of check_output() to handle non-zero exit codes
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=6
        )
        
        output = result.stdout.decode().strip()
        
        # If curl succeeded (exit code 0), we have connectivity
        if result.returncode == 0:
            try:
                time_seconds = float(output)
                time_ms = round(time_seconds * 1000, 1)
                return ("UP", time_ms)
            except ValueError:
                return ("UP", -1)
        else:
            # Connection failed
            return ("DOWN", -1)
            
    except subprocess.TimeoutExpired:
        return ("DOWN", -1)
    except Exception:
        return ("DOWN", -1)


def parse_ping_time(output):
    """Extract ping time from command output"""
    for line in output.splitlines():
        if "time=" in line:
            try:
                parts = line.split("time=")
                if len(parts) > 1:
                    time_str = parts[1].split()[0]
                    time_str = time_str.replace("ms", "")
                    return float(time_str)
            except (ValueError, IndexError):
                continue
    return -1


def write_log(data):
    file_exists = os.path.isfile("log.csv")
    with open("log.csv", "a", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "CPU", "Memory", "Disk", "Ping_Status", "Ping_ms"])
        writer.writerow(data)


if __name__ == "__main__":
    for _ in range(5):
        row = get_system_info()
        write_log(row)
        print("Logged:", row)
        time.sleep(10)