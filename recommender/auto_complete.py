async def autocomplete(query: str, existing_queries: list[str]) -> list[str]:
    matching_queries = [
        q
        for q in existing_queries
        if query.lower().strip() in q.lower().strip()
    ]

    sorted_queries = sorted(matching_queries, key=lambda x: len(x))
    return sorted_queries[:5]
