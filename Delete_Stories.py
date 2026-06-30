from jira import JIRA
from dotenv import load_dotenv
import os
import time

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = ""
PROJECT_KEY = "SCRUM"
START = 1
END = 404

jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

for i in range(START, END + 1):
    issue_key = f"{PROJECT_KEY}-{i}"
    try:
        print(f"Deleting {issue_key}...")
        issue = jira.issue(issue_key)
        issue.delete()
        time.sleep(0.1)  # avoid rate limit
    except Exception as e:
        print(f"Skipping {issue_key} (may not exist): {e}")

print("✅ Done deleting issues.")
