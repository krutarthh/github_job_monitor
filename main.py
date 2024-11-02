from flask import Flask, render_template_string
import requests
import time
import schedule
import os
from threading import Thread

# Replace with your GitHub token and the repos you want to monitor
GITHUB_TOKEN = ""
REPOS = ["IsaiahIruoha/Canadian-Tech-And-Business-Internships-Summer-2025",
         "HassanChowdhry/Canadian-Tech-Internships-2025",
         "Dannny-Babs/Canadian-Tech-Internships-2025",
         "jenndryden/Canadian-Tech-Internships-Summer-2024"]

# Initialize Flask app
app = Flask(__name__)

# Function to read the last event message for a specific repo
def read_last_event(repo):
    last_event_file = f'last_event_{repo.replace("/", "_")}.txt'
    if os.path.exists(last_event_file):
        with open(last_event_file, 'r') as file:
            return file.read().strip()
    return None

# Function to write the last event message for a specific repo
def write_last_event(repo, event_message):
    last_event_file = f'last_event_{repo.replace("/", "_")}.txt'
    with open(last_event_file, 'w') as file:
        file.write(event_message)

def check_github_activity():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    for repo in REPOS:
        url = f"https://api.github.com/repos/{repo}/events"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            events = response.json()
            latest_event_message = ""
            for event in events:
                if event['type'] == 'PushEvent':
                    latest_event_message = f"{event['payload']['commits'][0]['message']} from {repo}"
                    break

            # Retrieve last event for this specific repo
            last_events_message = read_last_event(repo)

            if latest_event_message and latest_event_message != last_events_message:
                print(f"Latest new posting: {latest_event_message}!")
                write_last_event(repo, latest_event_message)  # Update the last known event for this repo
        else:
            print(f"Failed to fetch events for {repo}, status code: {response.status_code}")

# Schedule the check every 5 minutes
schedule.every(0.05).minutes.do(check_github_activity)

# Background thread to keep running the schedule
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduling in a background thread
Thread(target=run_schedule, daemon=True).start()

# Flask route to display the latest commit messages for each repository
@app.route("/")
def index():
    latest_messages = {}
    for repo in REPOS:
        latest_messages[repo] = read_last_event(repo) or "No new updates."

    return render_template_string("""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <title>GitHub Activity Monitor</title>
        </head>
        <body>
            <div style="text-align: center; padding-top: 20px;">
                <h1>GitHub Activity Monitor</h1>
                <table border="1" style="margin: auto;">
                    <tr>
                        <th>Repository</th>
                        <th>Latest Commit Message</th>
                    </tr>
                    {% for repo, message in latest_messages.items() %}
                    <tr>
                        <td>{{ repo }}</td>
                        <td>{{ message }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </body>
        </html>
    """, latest_messages=latest_messages)

if __name__ == "__main__":
    print("Starting GitHub activity monitor...")
    app.run(debug=True)







