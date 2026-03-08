from rag_report import AnnualReportRAG

rag = AnnualReportRAG()

while True:

    query = input("\n🔍 Ask about the HSBC annual report: ")

    if query.lower() in ["exit", "quit"]:
        break

    answer, docs = rag.ask(query)

    print("\n🧠 Answer:")
    print(answer)

    print("\n📚 Sources:")
    for doc in docs:
        print("Page:", doc.metadata.get("page"))