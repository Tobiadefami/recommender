import asyncio
import json
import os

import aiohttp
from youtube_transcript_api import YouTubeTranscriptApi

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


async def fetch_comment_replies(session, parent_id, max_replies=5):
    replies_url = f"https://www.googleapis.com/youtube/v3/comments?part=snippet&parentId={parent_id}&maxResults={max_replies}&key={YOUTUBE_API_KEY}"
    async with session.get(replies_url) as response:
        replies_response = await response.json()

    replies = []
    for item in replies_response.get("items", []):
        reply = item["snippet"]
        replies.append(
            {
                "id": item["id"],
                "author": reply["authorDisplayName"],
                "text": reply["textDisplay"],
                "likes": reply["likeCount"],
                "published_at": reply["publishedAt"],
            }
        )
    return replies


async def fetch_video_comments(
    session, video_id, max_comments=5, max_replies=5
):
    comments_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId={video_id}&maxResults={max_comments}&key={YOUTUBE_API_KEY}"
    async with session.get(comments_url) as response:
        comments_response = await response.json()

    comments = []
    for item in comments_response.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]
        comment_data = {
            "id": item["snippet"]["topLevelComment"]["id"],
            "author": comment["authorDisplayName"],
            "text": comment["textDisplay"],
            "likes": comment["likeCount"],
            "published_at": comment["publishedAt"],
            "replies": [],
        }

        # Fetch replies if there are any
        if item["snippet"]["totalReplyCount"] > 0:
            if "replies" in item and "comments" in item["replies"]:
                # Replies are already included in the response
                for reply in item["replies"]["comments"]:
                    reply_snippet = reply["snippet"]
                    comment_data["replies"].append(
                        {
                            "id": reply["id"],
                            "author": reply_snippet["authorDisplayName"],
                            "text": reply_snippet["textDisplay"],
                            "likes": reply_snippet["likeCount"],
                            "published_at": reply_snippet["publishedAt"],
                        }
                    )
            else:
                # Fetch replies separately
                comment_data["replies"] = await fetch_comment_replies(
                    session, item["id"], max_replies
                )

        comments.append(comment_data)
    return comments


async def search_youtube_videos(
    query="pixel phone reviews", max_results=5, max_comments=5, max_replies=5
):
    async with aiohttp.ClientSession() as session:
        try:
            print("searching youtube...")
            search_url = f"https://www.googleapis.com/youtube/v3/search?part=id,snippet&q={query}&type=video&maxResults={max_results}&key={YOUTUBE_API_KEY}"
            async with session.get(search_url) as response:
                search_response = await response.json()

            videos = []
            for search_result in search_response.get("items", []):
                author = search_result["snippet"]["channelTitle"]
                video_id = search_result["id"]["videoId"]
                video_title = search_result["snippet"]["title"]
                video_description = search_result["snippet"]["description"]
                created_at = search_result["snippet"]["publishedAt"]

                # Get video statistics
                stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={YOUTUBE_API_KEY}"
                async with session.get(stats_url) as response:
                    video_response = await response.json()

                video_data = video_response["items"][0]
                print(video_data.keys())
                statistics = video_data["statistics"]

                # Get video transcript
                try:
                    transcript = await asyncio.to_thread(
                        YouTubeTranscriptApi.get_transcript, video_id
                    )
                    transcript_text = " ".join(
                        [entry["text"] for entry in transcript]
                    )
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
                    transcript_text = "Transcript not available"

                comments = await fetch_video_comments(
                    session, video_id, max_comments, max_replies
                )
                videos.append(
                    {
                        "author": author,
                        "id": video_id,
                        "title": video_title,
                        "description": video_description,
                        "views": statistics.get("viewCount"),
                        "likes": statistics.get("likeCount"),
                        "created_at": created_at,
                        "body": transcript_text,
                        "comments": comments,
                    }
                )

            return videos

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []


async def save_data(output_dir="recommender/data", query="pixel phone reviews"):
    output_path = os.path.join(output_dir, "youtube_data2.json")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    results = await search_youtube_videos(query)
    existing_data = {}
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            existing_data = json.load(f)

    existing_data.update(results)

    with open(output_path, "w") as f:
        json.dump(existing_data, f, indent=4)

    return existing_data


if __name__ == "__main__":
    asyncio.run(save_data())
