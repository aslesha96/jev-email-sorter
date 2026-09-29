import csv
import time

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

questions = {
    "folder": Choice(
        instructions="Which folder should this email go in?",
        criteria={
            "Work": "Job, colleagues, meetings, projects, deadlines",
            "Bills": "Invoices, payments, statements, subscriptions",
            "Shopping": "Orders, deliveries, sales, promotions",
            "Social": "Friends, family, invitations, social media",
            "Spam": "Scams, phishing, junk, suspicious offers",
        },
    ),
    "useful": Noul(
        instructions="Is this email useful, something the reader would want to read or act on?"
    ),
    "importance": Score(
        instructions="How important is this email to the reader?",
        criteria=["ignore", "read later", "read today", "read now"],
    ),
}

with open("emails.csv", newline="", encoding="utf-8") as f:
    emails = list(csv.DictReader(f))

results = []
total_chars = 0
start = time.time()

with TypeSafeClient() as client:
    for i, email in enumerate(emails, 1):
        state = {"subject": email["subject"], "body": email["body"]}
        total_chars += len(email["subject"]) + len(email["body"])
        response = client.system_one(state=state, questions=questions)
        folder = response.choices["folder"].choice
        useful = response.nouls["useful"].noul
        importance = response.scores["importance"].score
        results.append([email["id"], email["subject"], folder, round(useful, 2), round(importance, 1)])
        print(f"{i}/{len(emails)}  {folder:<9} {email['subject']}")

seconds = time.time() - start

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "subject", "folder", "useful", "importance"])
    writer.writerows(results)

est_tokens = total_chars / 4
est_cost = est_tokens / 1_000_000 * 0.042
print()
print(f"Sorted {len(emails)} emails in {seconds:.1f} seconds")
print(f"Estimated input tokens: {est_tokens:,.0f} (rough guess, plus the question text)")
print(f"Estimated cost: ${est_cost:.4f}")
print("Saved results to results.csv")