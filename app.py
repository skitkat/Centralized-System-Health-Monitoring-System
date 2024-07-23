from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

CSV_FILE_PATH = '/home/kali/Desktop/all_server_health.csv'

@app.route('/')
def index():
    # Load the CSV file into a DataFrame
    df = pd.read_csv(CSV_FILE_PATH)

    # Get the list of unique cities
    cities = df['Location'].unique()

    return render_template('index.html', cities=cities)

@app.route('/get_data', methods=['GET'])
def get_data():
    # Load the CSV file into a DataFrame
    df = pd.read_csv(CSV_FILE_PATH)

    # Get the selected city from the request
    selected_city = request.args.get('city')

    # Filter the DataFrame based on the selected city
    if selected_city and selected_city != 'All':
        df = df[df['Location'] == selected_city]

    # Add a 'color' column based on the thresholds
    df['color'] = df.apply(lambda row: get_color(row), axis=1)

    # Convert DataFrame to a list of dictionaries
    data = df.to_dict(orient='records')

    return jsonify(data)

def get_color(row):
    # Define thresholds and color coding logic
    try:
        # Check memory, CPU, and disk usage thresholds
        memory_usage = float(row['Memory Usage'].replace('%', ''))
        cpu_usage = float(row['CPU Usage'].replace('%', ''))
        disk_usage = float(row['Disk Usage'].replace('%', ''))

        # Determine the highest value among the three metrics
        highest_usage = max(memory_usage, cpu_usage, disk_usage)

        if highest_usage >= 90:
            return 'red'
        elif highest_usage >= 70:
            return 'orange'
        elif highest_usage >= 50:
            return 'yellow'
        else:
            return 'green'
    except ValueError:
        return 'green'  # Default to green if there's a parsing error

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, ssl_context=('certificate.pem', 'key.pem'))

