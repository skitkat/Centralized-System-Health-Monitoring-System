

# RHEL Server Network Monitoring System

## Project Description

The RHEL Server Network Monitoring System is designed to monitor and log system metrics from multiple remote servers in a central location. This system includes:

- A central server that receives and stores metrics from remote servers in a CSV file.
- A web-based dashboard built with Python Flask to visualize the collected data.

The application is useful for monitoring key system performance indicators such as disk usage, memory usage, and CPU usage across multiple servers, providing a centralized view of your network's health.

## Prerequisites

Before running the application, ensure you have the following:

1. **Python 3.7 or higher**: Required to run the Flask application and the metrics collection script.
2. **Flask**: Web framework used to build the dashboard.
3. **Pandas**: Library for data manipulation and analysis.
4. **Paramiko**: Library for SSH connections to remote servers.
5. **Requests**: Library for making HTTP requests.
6. **CSV File**: A CSV file (`all_server_health.csv`) on the central server to store metrics.
7. **SSH Access**: SSH access to the central server for uploading metrics.
8. **Permissions**: Ensure you have the necessary permissions to execute system commands and access the network.

## Installation

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Python Packages**

   Create a virtual environment (optional but recommended) and install the required packages:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install flask pandas paramiko requests
   ```

## Running the Application

1. **Start the Flask Web Application**

   Navigate to the directory containing `app.py` and run the following command:

   ```bash
   python app.py
   ```

   The Flask application will start and be accessible at `http://localhost:5000`.

2. **Run the Metrics Collection Script**

   On each remote server, run the `p.py` script to collect system metrics and send them to the central server:

   ```bash
   python p.py
   ```

   This script will gather system metrics, including disk usage, memory usage, CPU usage, and firewall rules, and upload them to the central server.

## Project Functionality

1. **Metrics Collection**: The `p.py` script collects system metrics from remote servers, including disk usage, memory usage, CPU usage, and firewall rules. It then sends this data to a central server.

2. **Data Storage**: Metrics are stored in a CSV file (`all_server_health.csv`) on the central server. This file is updated with new metrics or existing metrics are modified based on the IP address of the remote server.

3. **Web Dashboard**: The Flask web application (`app.py`) serves a dashboard that reads data from the CSV file and displays it in a table format. Users can select specific cities (or "All") to view metrics.

4. **Dynamic Row Coloring**: In the web dashboard, rows are colored based on the severity of system metrics. When "All" is selected, all rows are displayed with a default color, ignoring individual metric thresholds.

