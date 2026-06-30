from jira import JIRA
from dotenv import load_dotenv
import os
import random

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# IMPORTANT: set this to your Jira story points custom field id in .env
# Example: STORY_POINTS_FIELD=customfield_10016
STORY_POINTS_FIELD = os.getenv("STORY_POINTS_FIELD")

# Issue type (Story is often 10001 or similar; your earlier scripts used 10003)
ISSUE_TYPE_ID = os.getenv("ISSUE_TYPE_ID", "10003")

PROJECT_KEY = "SCRUM"
TOTAL_STORIES = 200

if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    raise RuntimeError("Please set JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN in .env")

jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

# -----------------------------
# Domain vocab
# -----------------------------
CHANNELS = ["mobile app", "web app", "dealer portal", "partner API"]
BUREAUS = ["Experian", "Equifax", "TransUnion"]
DOCS = ["income proof", "KYC document", "bank statement", "vehicle invoice"]
REGIONS = ["IN", "US", "EU"]
PAYMENT_METHODS = ["ACH", "UPI", "card", "netbanking"]

# -----------------------------
# Templates by complexity (deterministic SP)
# -----------------------------
TEMPLATES = {
    2: [
        {
            "summary": "Add UI validation for vehicle VIN field in {channel}",
            "desc": """
Auto Lending - Consumer Tech

Context:
- Channel: {channel}
- Module: vehicle details
- Change Type: UI validation

Requirement:
- Validate VIN length and allowed characters on client-side
- Show inline error message for invalid VIN
- Add unit tests for validation function

Acceptance Criteria:
Scenario: Enter valid VIN
  Given the user enters a VIN with valid length and format
  When the user submits vehicle details
  Then the system accepts the VIN and proceeds

Scenario: Enter invalid VIN
  Given the user enters an invalid VIN
  When the user submits vehicle details
  Then the system shows a validation error
  And the user cannot proceed
""".strip(),
        },
        {
            "summary": "Add audit log entry for loan application status change to {status}",
            "desc": """
Auto Lending - Consumer Tech

Context:
- Module: loan application
- Change Type: logging/audit

Requirement:
- On status change, write audit log with application id, old status, new status, timestamp
- Ensure logs are searchable by application id
- Add unit tests for audit logger

Acceptance Criteria:
Scenario: Status changes are logged
  Given a loan application status changes from A to {status}
  When the system updates the application
  Then an audit log entry is created with old and new status

Scenario: Audit log includes identifiers
  Given an audit log is created
  Then it includes application id and timestamp
""".strip(),
        },
    ],

    3: [
        {
            "summary": "Implement server-side validation for down payment percentage in {channel}",
            "desc": """
Auto Lending - Consumer Tech

Context:
- Channel: {channel}
- Module: pricing and eligibility
- Change Type: API validation

Requirement:
- Validate down payment is between 0% and 90%
- Return clear error message and error code
- Add unit tests and API integration tests

Acceptance Criteria:
Scenario: Valid down payment accepted
  Given the user provides a down payment between 0% and 90%
  When eligibility calculation is requested
  Then the system processes successfully

Scenario: Invalid down payment rejected
  Given the user provides a down payment outside the allowed range
  When eligibility calculation is requested
  Then the system rejects the request with a validation error
""".strip(),
        },
        {
            "summary": "Add retry with single backoff for {bureau} credit pull timeout",
            "desc": """
Auto Lending - Consumer Tech

Context:
- Module: credit bureau integration
- Bureau: {bureau}
- Change Type: resiliency (simple)

Requirement:
- If bureau call times out once, retry one time with backoff
- Log retry attempt with correlation id
- Add unit tests for retry behaviour

Acceptance Criteria:
Scenario: Timeout triggers retry
  Given the {bureau} credit pull times out
  When the system retries once
  Then the second attempt is executed with backoff
  And the retry is logged

Scenario: Retry fails
  Given the retry attempt also fails
  Then the system returns a controlled error response
""".strip(),
        },
    ],

    5: [
        {
            "summary": "Integrate vehicle valuation service and store valuation snapshot in database",
            "desc": """
Auto Lending - Consumer Tech

Context:
- Module: vehicle valuation
- Change Type: external integration + persistence

Requirement:
- Call valuation service using VIN, make, model, year
- Persist valuation response snapshot with version and timestamp
- Expose valuation in loan quote API response
- Add unit tests + integration tests
- Add failure handling with fallback message

Acceptance Criteria:
Scenario: Valuation retrieved and stored
  Given a valid VIN and vehicle details
  When the quote API requests valuation
  Then the system calls the valuation service
  And stores the valuation snapshot in the database

Scenario: Valuation included in quote
  Given valuation exists for the application
  When quote is generated
  Then the quote response includes valuation amount and timestamp

Scenario: Valuation service failure
  Given the valuation service is unavailable
  When quote is requested
  Then the system returns a fallback response
  And logs the error with correlation id
""".strip(),
        },
        {
            "summary": "Implement configurable eligibility rule for max DTI ratio by region {region}",
            "desc": """
Auto Lending - Consumer Tech

Context:
- Module: eligibility / risk rules
- Region: {region}
- Change Type: rule engine + config

Requirement:
- Add configuration-driven max DTI threshold by region
- Apply rule during pre-approval eligibility checks
- Store decision reason codes in database
- Add unit tests for rule evaluation + integration tests

Acceptance Criteria:
Scenario: Eligibility passes within DTI threshold
  Given an applicant with DTI below the configured threshold for {region}
  When eligibility is evaluated
  Then the applicant is marked eligible
  And decision reason codes are stored

Scenario: Eligibility fails beyond DTI threshold
  Given an applicant with DTI above the configured threshold for {region}
  When eligibility is evaluated
  Then the applicant is marked ineligible
  And decision reason codes are stored
""".strip(),
        },
    ],

    8: [
        {
            "summary": "Implement document verification workflow for {doc} with async status updates",
            "desc": """
Auto Lending - Consumer Tech

Context:
- Module: document verification
- Document type: {doc}
- Change Type: workflow + async + persistence

Requirement:
- Submit document to verification provider asynchronously
- Persist verification request + status transitions (PENDING, VERIFIED, FAILED)
- Provide status polling API for client apps
- Publish status updates to notification service
- Add unit tests + integration tests + failure handling

Acceptance Criteria:
Scenario: Document verification initiated
  Given a user uploads {doc}
  When verification is initiated
  Then the request is stored with status PENDING
  And a verification job is submitted to provider

Scenario: Verification status updates are persisted
  Given provider returns VERIFIED or FAILED
  When the system receives callback/status update
  Then the status is updated in the database
  And the status change is published to notifications

Scenario: Client can view status
  Given a verification request exists
  When client calls the status API
  Then the latest verification status is returned
""".strip(),
        },
        {
            "summary": "Create loan disbursement orchestration with idempotency and reconciliation",
            "desc": """
Auto Lending - Consumer Tech

Context:
- Module: loan disbursement
- Change Type: orchestration + idempotency + reconciliation

Requirement:
- Implement disbursement orchestration (initiate, confirm, settle)
- Ensure idempotency using a unique disbursement key
- Persist disbursement ledger and reconciliation status
- Provide admin endpoint to re-run reconciliation
- Add unit tests + integration tests, including retries and partial failure handling

Acceptance Criteria:
Scenario: Disbursement is idempotent
  Given a disbursement request with the same idempotency key is submitted twice
  When the system processes the request
  Then only one disbursement is created
  And the second request returns the same result

Scenario: Disbursement ledger is created
  Given a disbursement succeeds
  Then a ledger entry is stored with amounts and timestamps
  And reconciliation status is set to PENDING

Scenario: Reconciliation can be re-run
  Given reconciliation failed earlier
  When an admin triggers reconciliation rerun
  Then reconciliation executes again
  And status is updated accordingly
""".strip(),
        },
    ],
}

# Deterministic distribution: mostly 5 and 8, few 2 and 3
# Total = 200
PLAN = (
    [5] * 85 +   # 85 stories
    [8] * 85 +   # 85 stories
    [3] * 15 +   # 15 stories
    [2] * 15     # 15 stories
)

assert len(PLAN) == TOTAL_STORIES


def render(template: dict) -> (str, str):
    # Fill placeholders used by templates
    channel = random.choice(CHANNELS)
    bureau = random.choice(BUREAUS)
    doc = random.choice(DOCS)
    region = random.choice(REGIONS)
    status = random.choice(["SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"])

    summary = template["summary"].format(
        channel=channel, bureau=bureau, doc=doc, region=region, status=status
    )
    desc = template["desc"].format(
        channel=channel, bureau=bureau, doc=doc, region=region, status=status
    )
    return summary, desc


def create_stories():
    print(f"Creating {TOTAL_STORIES} Auto Lending stories in project {PROJECT_KEY}...")

    # Shuffle story order, but SP is still determined by the chosen bucket
    random.shuffle(PLAN)

    for i, sp in enumerate(PLAN, start=1):
        template = random.choice(TEMPLATES[sp])
        summary, description = render(template)

        fields = {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"id": ISSUE_TYPE_ID},
            "labels": ["AUTO_LENDING", "CONSUMER_TECH", "GENAI_TEST"],
        }

        if STORY_POINTS_FIELD:
            fields[STORY_POINTS_FIELD] = sp

        issue = jira.create_issue(fields=fields)
        print(f"[{i}/{TOTAL_STORIES}] Created {issue.key} (SP={sp})")

    print("✅ Done creating stories.")


if __name__ == "__main__":
    create_stories()