import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import aiohttp
from youtube_transcript_api import YouTubeTranscriptApi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


@asynccontextmanager
async def get_youtube_session():
    """Context manager for YouTube API session"""
    async with aiohttp.ClientSession() as session:
        try:
            yield session
        finally:
            if not session.closed:
                await session.close()


async def get_transcript(video_id: str) -> Optional[str]:
    """
    Get video transcript.

    Args:
        video_id: YouTube video ID

    Returns:
        String containing the transcript or None if unavailable
    """
    try:
        transcript = await asyncio.to_thread(
            YouTubeTranscriptApi.get_transcript, video_id
        )
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        logger.error(f"Transcript error for video {video_id}: {str(e)}")
        return None


async def fetch_comment_replies(
    session: aiohttp.ClientSession, parent_id: str, max_replies: int = 5
) -> List[Dict]:
    """
    Fetch replies for a specific comment.

    Args:
        session: Active aiohttp session
        parent_id: ID of the parent comment
        max_replies: Maximum number of replies to fetch

    Returns:
        List of reply dictionaries
    """
    try:
        replies_url = (
            "https://www.googleapis.com/youtube/v3/comments"
            f"?part=snippet&parentId={parent_id}"
            f"&maxResults={max_replies}&key={YOUTUBE_API_KEY}"
        )

        async with session.get(replies_url) as response:
            if response.status != 200:
                logger.error(
                    f"Error fetching replies: {response.status} - {await response.text()}"
                )
                return []

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
                    "url": f"https://www.youtube.com/watch?v={reply['videoId']}&lc={item['id']}",
                }
            )
        return replies

    except Exception as e:
        logger.error(f"Error fetching comment replies: {str(e)}")
        return []


async def fetch_video_comments(
    session: aiohttp.ClientSession,
    video_id: str,
    max_comments: int = 5,
    max_replies: int = 5,
) -> List[Dict]:
    """
    Fetch comments for a specific video.

    Args:
        session: Active aiohttp session
        video_id: YouTube video ID
        max_comments: Maximum number of comments to fetch
        max_replies: Maximum number of replies per comment

    Returns:
        List of comment dictionaries
    """
    try:
        comments_url = (
            "https://www.googleapis.com/youtube/v3/commentThreads"
            f"?part=snippet,replies&videoId={video_id}"
            f"&maxResults={max_comments}&key={YOUTUBE_API_KEY}"
        )

        async with session.get(comments_url) as response:
            if response.status != 200:
                logger.error(
                    f"Error fetching comments: {response.status} - {await response.text()}"
                )
                return []

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
                "url": f"https://www.youtube.com/watch?v={video_id}&lc={item['id']}",
                "replies": [],
            }

            # Handle replies
            if item["snippet"]["totalReplyCount"] > 0:
                if "replies" in item and "comments" in item["replies"]:
                    # Use existing replies in response
                    for reply in item["replies"]["comments"]:
                        reply_snippet = reply["snippet"]
                        comment_data["replies"].append(
                            {
                                "id": reply["id"],
                                "author": reply_snippet["authorDisplayName"],
                                "text": reply_snippet["textDisplay"],
                                "likes": reply_snippet["likeCount"],
                                "published_at": reply_snippet["publishedAt"],
                                "url": f"https://www.youtube.com/watch?v={video_id}&lc={reply['id']}",
                            }
                        )
                else:
                    # Fetch replies separately
                    comment_data["replies"] = await fetch_comment_replies(
                        session, item["id"], max_replies
                    )

            comments.append(comment_data)
            logger.info(f"Processed comment: {comment_data['url']}")

        return comments

    except Exception as e:
        logger.error(f"Error fetching video comments: {str(e)}")
        return []


async def search_youtube_videos(
    query: str,
    max_results: int = 5,
    max_comments: int = 5,
    max_replies: int = 5,
) -> List[Dict]:
    """
    Search YouTube for videos and fetch their details.

    Args:
        query: Search query string
        max_results: Maximum number of videos to return
        max_comments: Maximum number of comments per video
        max_replies: Maximum number of replies per comment

    Returns:
        List of video dictionaries with details
    """
    async with get_youtube_session() as session:
        try:
            logger.info(f"Searching YouTube for: {query}")

            # Search for videos
            search_url = (
                "https://www.googleapis.com/youtube/v3/search"
                f"?part=id,snippet&q={query}&type=video"
                f"&maxResults={max_results}&key={YOUTUBE_API_KEY}"
            )

            async with session.get(search_url) as response:
                if response.status != 200:
                    logger.error(
                        f"Search error: {response.status} - {await response.text()}"
                    )
                    return []

                search_response = await response.json()

            videos = []
            for search_result in search_response.get("items", []):
                try:
                    video_id = search_result["id"]["videoId"]
                    video_info = search_result["snippet"]

                    # Get video statistics
                    stats_url = (
                        "https://www.googleapis.com/youtube/v3/videos"
                        f"?part=statistics&id={video_id}&key={YOUTUBE_API_KEY}"
                    )

                    async with session.get(stats_url) as response:
                        if response.status != 200:
                            logger.error(
                                f"Stats error: {response.status} - {await response.text()}"
                            )
                            continue

                        video_response = await response.json()

                    if not video_response.get("items"):
                        logger.error(
                            f"No statistics found for video {video_id}"
                        )
                        continue

                    video_data = video_response["items"][0]
                    statistics = video_data["statistics"]

                    # Get transcript
                    transcript_text = (
                        await get_transcript(video_id)
                        or "Transcript not available"
                    )

                    # Get comments
                    comments = await fetch_video_comments(
                        session, video_id, max_comments, max_replies
                    )

                    videos.append(
                        {
                            "author": video_info["channelTitle"],
                            "id": video_id,
                            "title": video_info["title"],
                            "description": video_info["description"],
                            "views": statistics.get("viewCount"),
                            "likes": statistics.get("likeCount"),
                            "created_at": video_info["publishedAt"],
                            "body": transcript_text,
                            "comments": comments,
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                        }
                    )
                    logger.info(f"Processed video: {videos[-1]['url']}")

                except Exception as e:
                    logger.error(f"Error processing video {video_id}: {str(e)}")
                    continue

            return videos

        except Exception as e:
            logger.error(f"Error in YouTube search: {str(e)}")
            return []


if __name__ == "__main__":
    asyncio.run(search_youtube_videos("pixel phone reviews"))
