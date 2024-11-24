from typing import Dict


def filter_data(db: Dict[str, list[dict]]) -> Dict[str, list[dict]]:
    modified = [
        data for data in db["reviews"] if data.get("review_summary") is not None
    ]
    db["reviews"] = modified
    return db
