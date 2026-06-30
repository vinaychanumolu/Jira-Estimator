from jira import JIRA
from dotenv import load_dotenv
import os
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("PROJECT_KEY", "SCRUM")
STORY_POINTS_FIELD = os.getenv("STORY_POINTS_FIELD")

jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

client = chromadb.PersistentClient(path="./chroma_jira")
collection = client.get_or_create_collection("jira_stories")
model = SentenceTransformer("all-MiniLM-L6-v2")


def fetch_issues():
    jql = (
        f'project = {PROJECT_KEY} '
        f'AND issuekey >= {PROJECT_KEY}-205 '
        f'AND issuekey <= {PROJECT_KEY}-404 '
        f'ORDER BY created ASC'
    )

    issues = jira.search_issues(jql_str=jql, maxResults=500)
    ids, docs, metas = [], [], []

    for issue in issues:
        f = issue.fields
        text = (f.summary or "") + "\n" + (f.description or "")
        if not text.strip():
            continue

        sp = getattr(f, STORY_POINTS_FIELD, None) if STORY_POINTS_FIELD else None

        ids.append(issue.key)
        docs.append(text)
        metas.append(
            {
                "key": issue.key,
                "summary": f.summary or "",
                "story_points": sp,
                "status": str(f.status.name),
            }
        )
    return ids, docs, metas


def build():
    print(f"Fetching Jira issues from {PROJECT_KEY}...")
    ids, docs, metas = fetch_issues()
    print(f"Got {len(docs)} issues with text.")

    if not docs:
        print("No issues with text found.")
        return

    print("Creating embeddings...")
    embeddings = model.encode(docs, convert_to_numpy=False)

    # Clear old data safely
    try:
        existing = collection.get(limit=100000)
        old_ids = existing.get("ids", [])
        if old_ids:
            collection.delete(ids=old_ids)
            print(f"Deleted {len(old_ids)} old embeddings.")
    except Exception as e:
        print("Warning during delete:", e)

    print("Adding to Chroma...")
    collection.add(
        ids=ids,
        documents=docs,
        embeddings=[e.tolist() for e in embeddings],
        metadatas=metas,
    )

    print("✅ Done. Collection now has", collection.count(), "documents.")


if __name__ == "__main__":
    build()
