import json
from pathlib import Path
import os
from  filter_data import process_text_for_product_review

def save_reddit_data(submissions, search_query, filename='reddit_data.json'):
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    file_path = data_dir / filename
    existing_data = load_existing_data(file_path)
    updated_data = add_new_submissions(existing_data, search_query, submissions)
    save_updated_data(file_path, updated_data)

def load_existing_data(file_path):
    if file_path.exists():
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

def add_new_submissions(existing_data, search_query, submissions):
    for submission in submissions:
        submission_data = create_submission_data(submission, search_query)
        existing_data.append(submission_data)
    return existing_data

def create_submission_data(submission, search_query):
    return {
        'search_query': search_query,
        'id': submission.id,
        'title': submission.title,
        'score': submission.score,
        'url': submission.url,
        'num_comments': submission.num_comments,
        'created': submission.created,
        'body': submission.selftext,
        "is_product_review": process_text_for_product_review(submission.selftext)
    }

def save_updated_data(file_path, data):
    # TODO: switch this to use the models defined in models.py and store as part of the DB
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
