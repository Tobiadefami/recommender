import asyncio
import json
import os

import aiohttp
from youtube_transcript_api import YouTubeTranscriptApi

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


async def search_youtube_videos(query="pixel phone reviews", max_results=5):
    async with aiohttp.ClientSession() as session:
        try:
            print("searching...")
            search_url = f"https://www.googleapis.com/youtube/v3/search?part=id,snippet&q={query}&type=video&maxResults={max_results}&key={YOUTUBE_API_KEY}"
            async with session.get(search_url) as response:
                search_response = await response.json()

            videos = []
            for search_result in search_response.get("items", []):
                video_id = search_result["id"]["videoId"]
                video_title = search_result["snippet"]["title"]
                video_description = search_result["snippet"]["description"]

                # Get video statistics
                stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={YOUTUBE_API_KEY}"
                async with session.get(stats_url) as response:
                    video_response = await response.json()

                statistics = video_response["items"][0]["statistics"]

                # Get video transcript
                try:
                    transcript = await asyncio.to_thread(
                        YouTubeTranscriptApi.get_transcript, video_id
                    )
                    transcript_text = " ".join(
                        [entry["text"] for entry in transcript]
                    )
                except:
                    transcript_text = "Transcript not available"

                videos.append(
                    {
                        "id": video_id,
                        "title": video_title,
                        "description": video_description,
                        "views": statistics.get("viewCount"),
                        "likes": statistics.get("likeCount"),
                        "transcript": transcript_text,
                    }
                )

            return {query: videos}

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
