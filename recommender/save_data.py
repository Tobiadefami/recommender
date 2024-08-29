import json
from pathlib import Path
import os
from  recommender.structured_data import process_text_for_product_review
from praw.models import Comment

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

def add_new_submissions(existing_data, search_query, submissions, top_k=20):

    if search_query not in existing_data:
        existing_data[search_query] = []

    non_empty_submissions = []
    sorted_submission = sorted(submissions, key=lambda x: len(x.selftext), reverse=True)
    for submission in sorted_submission:
        if submission.selftext.strip():
            submission_data = create_submission_data(submission, search_query)
            non_empty_submissions.append(submission_data)
    existing_data[search_query].extend(non_empty_submissions)
    return existing_data

def create_submission_data(submission, search_query, depth:int=0, max_depth:int=3):
    # analysis = process_text_for_product_review(submission.selftext)
    # print(f"{analysis=}")
    def get_comments(comment_forest, depth, max_depth):
        if depth >=max_depth:
            return []

        comments = []

        for comment in comment_forest:
            if isinstance(comment, Comment):
                comments.append({'author': comment.author.name if comment.author else '[deleted]',
                'body': comment.body,
                'score': comment.score,
                'created': comment.created,
                'replies': sorted(get_comments(comment.replies, depth+1, max_depth) , key=lambda x: x['score'], reverse=True)
                })
        return comments

    comments = get_comments(submission.comments, depth, max_depth)
    sorted_comments = sorted(comments, key=lambda x: x['score'], reverse=True)

    return {
        'user': submission.author.name if submission.author else '[deleted]',
        'id': submission.id,
        'title': submission.title,
        'score': submission.score,
        'url': submission.url,
        'num_comments': submission.num_comments,
        'created': submission.created,
        'body': submission.selftext,
        'comments':sorted_comments
        }

def save_updated_data(file_path, data):
    # TODO: switch this to use the models defined in models.py and store as part of the DB
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
