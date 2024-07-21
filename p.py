import paramiko
import requests
import subprocess
import datetime
import pandas as pd
import io

# Variables
CENTRAL_SERVER_IP = "192.168.37.149"
CENTRAL_SERVER_USER = "kali"
CENTRAL_SERVER_PASS = "kali"
REMOTE_FILE_PATH = "/home/kali/Desktop/all_server_health.csv"

# Function to get geographical location based on IP
def get_geo_location():
    try:
        response = requests.get("http://ipinfo.io/json")
        response.raise_for_status()
        city = response.json().get("city", "Unknown")
        return city
    except requests.RequestException as e:
        print(f"Error fetching geo-location: {e}")
        return "Unknown"

# Function to get system metrics
def get_metrics():
    try:
        TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        DEVICE_NAME = subprocess.check_output(["hostname"]).strip().decode()
        NODE_IP = subprocess.check_output(["hostname", "-I"]).split()[0].decode()
        GEO_LOCATION = get_geo_location()
        TOTAL_DISK = subprocess.check_output("df -h / | awk 'NR==2 {print $2}'", shell=True).strip().decode()
        DISK_USAGE = subprocess.check_output("df -h / | awk 'NR==2 {print $5}' | sed 's/%//g'", shell=True).strip().decode()
        TOTAL_MEMORY = subprocess.check_output("free -h | grep Mem | awk '{print $2}'", shell=True).strip().decode()
        MEMORY_USAGE = subprocess.check_output("free | grep Mem | awk '{print $3/$2 * 100.0}' | awk '{printf \"%.2f\", $1}'", shell=True).strip().decode()
        CPU_USAGE = subprocess.check_output("top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}' | awk '{printf \"%.2f\", $1}'", shell=True).strip().decode()
        NO_OF_CPU = subprocess.check_output("nproc", shell=True).strip().decode()
        
        # Limit firewall rules to the first 5 rules
        FIREWALL_RULES = subprocess.check_output("sudo iptables -L | head -n 5 | tr '\\n' ' ' | sed 's/\"/\"\"/g'", shell=True).strip().decode()

        METRICS = {
            'Timestamp': TIMESTAMP,
            'Location': GEO_LOCATION,
            'IP': NODE_IP,
            'Total Disk': TOTAL_DISK,
            'Disk Usage': f"{DISK_USAGE}%",
            'Total Memory': TOTAL_MEMORY,
            'Memory Usage': f"{MEMORY_USAGE}%",
            'CPU Usage': f"{CPU_USAGE}%",
            'Number of CPUs': NO_OF_CPU,
            'Firewall Rules': FIREWALL_RULES
        }
        return METRICS

    except subprocess.CalledProcessError as e:
        print(f"Error getting metrics: {e}")
        return {}

# Function to send metrics to central server
def send_metrics():
    METRICS = get_metrics()
    if not METRICS:
        print("No metrics to send.")
        return

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(CENTRAL_SERVER_IP, username=CENTRAL_SERVER_USER, password=CENTRAL_SERVER_PASS)

        # Download the existing CSV file from the central server
        sftp = ssh.open_sftp()
        try:
            with sftp.file(REMOTE_FILE_PATH, 'r') as remote_file:
                csv_content = remote_file.read().decode()
                df = pd.read_csv(io.StringIO(csv_content))
                print("CSV Columns:", df.columns)  # Debugging: Print columns

                # Define expected headers
                expected_headers = ['Timestamp', 'Location', 'IP', 'Total Disk', 'Disk Usage', 'Total Memory', 'Memory Usage', 'CPU Usage', 'Number of CPUs', 'Firewall Rules']
                
                # Check if headers are present
                if not all(header in df.columns for header in expected_headers):
                    print("CSV headers are incorrect or missing. Creating new file with correct headers.")
                    df = pd.DataFrame(columns=expected_headers)
                else:
                    df = df[expected_headers]

        except FileNotFoundError:
            print("CSV file not found, creating new DataFrame with headers.")
            df = pd.DataFrame(columns=['Timestamp', 'Location', 'IP', 'Total Disk', 'Disk Usage', 'Total Memory', 'Memory Usage', 'CPU Usage', 'Number of CPUs', 'Firewall Rules'])
        
        # Convert METRICS to DataFrame
        metrics_df = pd.DataFrame([METRICS])

        # Check and update DataFrame
        ip = METRICS['IP']
        if ip in df['IP'].values:
            # Update existing row
            df = df[df['IP'] != ip]  # Remove existing row
        # Append new row
        df = pd.concat([df, metrics_df], ignore_index=True)

        # Write updated DataFrame to a new CSV
        updated_csv = io.StringIO()
        df.to_csv(updated_csv, index=False)
        updated_csv.seek(0)

        # Upload the updated CSV file to the central server
        with sftp.file(REMOTE_FILE_PATH, 'w') as remote_file:
            remote_file.write(updated_csv.getvalue())

        ssh.close()
        print("Metrics successfully sent to central server.")
    
    except paramiko.SSHException as e:
        print(f"Error connecting to the central server: {e}")

# Collect and send metrics
send_metrics()

