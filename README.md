# AI-Powered Product Recommendation System

![Recommender System](/assets/recommender.png)

This project is an AI-powered product recommendation system that leverages data from Reddit and YouTube to provide structured information for making informed purchasing decisions. The system analyzes reviews, comments, and discussions to extract insights about products, helping users understand the pros and cons before making a purchase.

## Overview

The system consists of three main components:

1. **Backend (Recommender)**: A Python-based service that handles data collection, AI processing, and API endpoints.
2. **Frontend**: A Next.js web application that provides a user interface for interacting with the system.
3. **Nginx**: A reverse proxy that routes requests between the frontend and backend.

## Features

- User authentication and account management
- Reddit integration for collecting product discussions
- YouTube data collection for video reviews and comments
- AI-powered analysis of product reviews
- Structured output with pros, cons, and overall recommendations
- Search history and analytics

## Prerequisites

- Docker and Docker Compose
- uv (for local backend development)
- Node.js and npm (for local frontend development)
- GitHub account (for cloning the repository)
- Reddit API credentials (for Reddit integration)
- YouTube API key (for YouTube integration)
- OpenAI API key (for AI processing)

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/product-recommendation-system.git
cd product-recommendation-system
```

### 2. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```
# Database
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=recommender_db

# Backend
RECOMMENDER_ENV=development
JWT_SECRET_KEY=your_jwt_secret_key
NGINX_HOST=localhost:8080

# Reddit API
REDDIT_APP_CLIENT_ID=your_reddit_client_id
REDDIT_APP_CLIENT_SECRET=your_reddit_client_secret

# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Optional: Exa API (for enhanced search)
EXA_API_KEY=your_exa_api_key
```

### 3. Build and Run with Docker Compose

```bash
docker compose build
docker compose up -d
```

This will build and start all the necessary containers:
- PostgreSQL database
- Recommender backend
- Next.js frontend
- Nginx reverse proxy

### 4. Access the Application

Once all containers are running, you can access the application at:

```
http://localhost:8080
```

## Local Development

Install the Python backend dependencies with uv:

```bash
uv sync
uv run uvicorn recommender.app:app --reload
```

Install the frontend dependencies with npm:

```bash
cd frontend
npm install
npm run dev
```

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│             │      │             │      │             │
│   Frontend  │◄────►│    Nginx    │◄────►│  Recommender│
│  (Next.js)  │      │             │      │  (Backend)  │
│             │      │             │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │             │
                                          │  PostgreSQL │
                                          │  Database   │
                                          │             │
                                          └─────────────┘
```

## API Endpoints

The backend provides several API endpoints:

- `/api/search?query=<product_name>`: Search for product reviews and analysis
- `/api/register`: Register a new user
- `/api/token`: Get authentication token
- `/api/users/me`: Get current user information
- `/api/reddit/status`: Check Reddit authentication status
- `/api/user/recent-searches`: Get user's recent searches with analytics

## Technology Stack

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- SQLAlchemy
- Langchain
- OpenAI API
- Async PRAW (Reddit API)
- YouTube Data API

### Infrastructure
- Docker & Docker Compose
- PostgreSQL
- Nginx

## Development Status

This project is still a work in progress. Current limitations include:

- Limited product categories
- Occasional inaccuracies in AI analysis
- Performance optimizations needed for large datasets

Contributions are welcome to help improve the system!

## License

[MIT License](LICENSE)

## Acknowledgements

- Reddit API for providing access to community discussions
- YouTube API for video content
- OpenAI for AI processing capabilities
- Next.js and React for the frontend framework
- FastAPI for the backend framework
