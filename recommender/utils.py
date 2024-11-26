from typing import Dict


def filter_data(
    db: Dict[str, list[dict]], search_query
) -> Dict[str, list[dict]]:
    print(f"{db.keys()=}")
    print(f"{db[search_query].keys()=}")
    modified = [
        data
        for data in db[search_query]["reviews"]
        if data.get("review_summary") is not None
    ]
    db["reviews"] = modified
    return db
