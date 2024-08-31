import json
from pathlib import Path
import os
from  recommender.structured_data import process_post_for_product_review
from praw.models import Comment
from recommender.process_comments import process_comments
from recommender.process_submissions import process_submission, process_submissions


def save_reddit_data(submissions, search_query, filename='reddit_data.json'):
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    file_path = data_dir / filename
    existing_data = load_existing_data(file_path)
    updated_data = add_new_submissions(existing_data, search_query, submissions)
    save_updated_data(file_path, updated_data)

def load_existing_data(file_path):
    if file_path.exists():
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Error loading {file_path}")
            return {}
    return {}

def add_new_submissions(existing_data, search_query, submissions, score_threshold=10, min_length=50, recent_days=None):
    if search_query not in existing_data:
        existing_data[search_query] = []

    processed_submissions = process_submissions(submissions, score_threshold, min_length, recent_days)

    for submission in processed_submissions:
        submission_data = process_submission(
            submission,
            search_query,
            score_threshold=score_threshold,
            min_length=min_length,
            recent_days=recent_days
        )
        if submission_data:
            existing_data[search_query].append(submission_data)

    return existing_data



def save_updated_data(file_path, data):
    # TODO: switch this to use the models defined in models.py and store as part of the DB
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
