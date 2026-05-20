import sqlite3
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

# Schema description — this is what Claude uses to write correct SQL
SCHEMA = """
Database: library.db (SQLite)

Table: checkouts
- UsageClass (TEXT): 'Digital' or 'Physical'
- CheckoutType (TEXT): the platform used, e.g. 'Horizon', 'OverDrive'
- MaterialType (TEXT): item type, e.g. 'BOOK', 'EBOOK', 'SOUNDDISC', 'AUDIOBOOK'
- CheckoutYear (INTEGER): year of checkout, e.g. 2016
- CheckoutMonth (INTEGER): month of checkout, 1-12
- Checkouts (INTEGER): number of times this item was checked out in that month
- Title (TEXT): title of the item
- ISBN (TEXT): ISBN identifier, may be empty
- Creator (TEXT): author or creator name
- Subjects (TEXT): comma-separated subject tags
- Publisher (TEXT): publisher name
- PublicationYear (TEXT): year of publication, stored as text
"""

def generate_sql(question: str) -> str:
    """Ask Claude to convert a natural-language question into SQL."""
    prompt = f"""You are a SQL expert. Given the following SQLite database schema, write a SQL query to answer the user's question.

{SCHEMA}

Rules:
- Return ONLY the SQL query, no explanation, no markdown code fences, no commentary.
- Use SQLite syntax.
- If the question is ambiguous, make a reasonable interpretation.
- Limit results to 20 rows unless the question explicitly asks otherwise.

Question: {question}

SQL:"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def run_sql(sql: str):
    """Execute the SQL against the database and return the result."""
    conn = sqlite3.connect("library.db")
    try:
        result = pd.read_sql(sql, conn)
        return result
    except Exception as e:
        return f"SQL ERROR: {e}"
    finally:
        conn.close()


def ask(question: str):
    """Full pipeline: question → SQL → result, printed nicely."""
    print(f"\n{'='*70}")
    print(f"QUESTION: {question}")
    print('='*70)
    
    sql = generate_sql(question)
    print(f"\nGenerated SQL:\n{sql}\n")
    
    result = run_sql(sql)
    print("Result:")
    print(result)


# ---------- Evaluation set ----------
TEST_QUESTIONS = [
    "What are the top 5 most checked-out titles overall?",
    "How many digital vs physical checkouts were there in 2016?",
    "Which MaterialType has the highest total checkouts?",
    "What is the average number of checkouts per item?",
    "Show monthly checkout totals for the year 2016.",
    "Which publisher appears most often in the dataset?",
    "Find the top 10 creators by total checkouts.",
    "How many unique titles are there?",
    "What percentage of checkouts are digital?",
    "What are the top 5 most checked-out ebooks specifically?",
]

if __name__ == "__main__":
    results_log = []
    for i, q in enumerate(TEST_QUESTIONS, 1):
        print(f"\n\n########## TEST {i}/{len(TEST_QUESTIONS)} ##########")
        try:
            sql = generate_sql(q)
            result = run_sql(sql)
            success = not (isinstance(result, str) and result.startswith("SQL ERROR"))
            results_log.append({
                "question": q,
                "sql": sql,
                "sql_ran_successfully": success,
                "result_preview": str(result)[:200]
            })
            print(f"QUESTION: {q}")
            print(f"\nSQL:\n{sql}")
            print(f"\nResult:\n{result}")
        except Exception as e:
            results_log.append({
                "question": q,
                "sql": "N/A",
                "sql_ran_successfully": False,
                "result_preview": f"EXCEPTION: {e}"
            })
            print(f"FAILED: {e}")
    
    # Save the log
    pd.DataFrame(results_log).to_csv("evaluation_results.csv", index=False)
    
    # Print summary
    successes = sum(1 for r in results_log if r["sql_ran_successfully"])
    print(f"\n\n{'='*70}")
    print(f"FINAL SCORE: {successes}/{len(TEST_QUESTIONS)} questions produced valid SQL")
    print(f"Results saved to evaluation_results.csv")
    print('='*70)