from text_to_sql import ask

print("=" * 70)
print("LIBRARY DATABASE CHAT")
print("Ask any question about Seattle library checkouts.")
print("Type 'quit' or 'exit' to leave.")
print("=" * 70)

while True:
    print()
    question = input("Your question: ").strip()
    
    if question.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    
    if not question:
        continue
    
    try:
        ask(question)
    except Exception as e:
        print(f"Something went wrong: {e}")
        print("Try rephrasing the question.")