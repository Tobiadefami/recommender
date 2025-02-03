from typing import Dict


def filter_data(db: Dict[str, list[dict]]) -> Dict[str, list[dict]]:
    filtered_data = [
        data for data in db["reviews"] if data.get("review_summary") is not None
    ]
    db["reviews"] = filtered_data
    return db


async def autocomplete(query: str, existing_queries: list[str]) -> list[str]:
    matching_queries = [
        q
        for q in existing_queries
        if query.lower().strip() in q.lower().strip()
    ]

    sorted_queries = sorted(matching_queries, key=lambda x: len(x))
    return sorted_queries[:5]
