# Text-to-SQL Over Seattle Library Checkouts

A Python pipeline that converts natural-language questions into SQL queries using Claude's API, then executes them with a SQLite database of ~100,000 Seattle Public Library checkout records.

## What it does

Ask a question in plain English. Get back a real answer from the database.

Question: What are the top 5 most checked-out titles overall?
Generated SQL:
SELECT Title, SUM(Checkouts) AS TotalCheckouts
FROM checkouts
GROUP BY Title
ORDER BY TotalCheckouts DESC
LIMIT 5;

Result:
                                               Title  TotalCheckouts
0  Bridge of spies [videorecording] / Touchstone ...             377
1                                      The Economist             344
2  The revenant [videorecording] / 20th Century F...             340
3  Brooklyn [videorecording] / Fox Searchlight Pi...             326
4  Deadpool [videorecording] / Twentieth Century ...             300

## Why I built this

The TikTok / ByteDance AI/LLM Data Application team brief mentions applying LLMs to "knowledge Q&A and data analysis" scenarios. This project is a minimum working version of that idea: replace hand-written SQL with natural-language questions, while keeping the database as the source of truth.

The same pattern powers internal analytics tooling at Snowflake, Databricks, and ByteDance's Doubao.

## Stack

- **Python 3.13** — orchestration
- **Anthropic Claude API** (`claude-haiku-4-5`) — natural language to SQL
- **SQLite** — local relational store
- **pandas** — result handling
- **Source data:** Seattle Public Library checkout records (subset of 100,000 rows from the public Open Data portal)

## Architecture

User question (English)
↓
Prompt + schema description sent to Claude
↓
Claude returns SQL only
↓
Python executes SQL against SQLite
↓
Result returned as a pandas DataFrame

The schema is described in the prompt so Claude knows the exact column names and types — this prevents hallucinated columns, which is the most common failure mode for naive text-to-SQL.

## Evaluation

I tested 10 questions covering aggregation, filtering, grouping, percentages, and string filters. For each one I hand-wrote a reference SQL query and compared its output to the LLM-generated SQL's output.

**Results: 10/10 produced valid SQL that matched my reference output.**

The test set is in `text_to_sql.py` under `TEST_QUESTIONS`. The full log is saved to `evaluation_results.csv` on each run.

## Honest limitations

- Only 100,000 rows used (full dataset is ~3M). Performance characteristics on larger data not tested.
- No retry / self-correction loop — if Claude generates broken SQL, the script just reports the error rather than asking Claude to fix it.
- No handling of ambiguous questions — Claude picks one interpretation. A production version would ask a clarifying follow-up.
- Single-table schema. Real-world text-to-SQL gets harder with joins across many tables.

## How to run

1. Clone the repo
2. `python3 -m venv venv && source venv/bin/activate`
3. `pip install anthropic python-dotenv pandas`
4. Add your Anthropic API key to a `.env` file: `ANTHROPIC_API_KEY=sk-ant-...`
5. Download a CSV from https://data.seattle.gov/Community-and-Culture/Checkouts-by-Title/tmmm-ytt6 and save as `library.csv`
6. Build the database: `python build_database.py`
7. Run the pipeline: `python text_to_sql.py`

## Author

Zihao Wu (Oli) — UNSW Bachelor of Science (Statistics).