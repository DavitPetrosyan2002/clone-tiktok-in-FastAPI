# Video Subscription Web Application

## Description

This is a web application for video sharing, where users can subscribe to others, post videos, comment on them, and interact with content (like TikTok/Instagram-style). The application uses FastAPI as the backend framework and SQLAlchemy as the ORM, with a responsive frontend built with HTML, CSS, and JavaScript.

## Features

- **User Authentication**: Users can sign up, log in, and log out. Authentication is based on username and password.
- **Video Sharing**: Users can upload videos. Each video has metadata such as a title and description.
- **Subscriptions**: Users can subscribe to others and view their subscribers.
- **Comments**: Users can comment on videos. Comments are displayed dynamically, and the comment section expands when activated.
- **Video Player**: Custom video player functionality, including swipe gestures (up/down) for switching between videos.
- **Mobile-First Design**: The UI is responsive and optimized for mobile devices, with support for touch gestures.
- **Like System**: Users can like videos, and a list of users who liked a video is displayed.

## Technologies

- **Backend**: FastAPI, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Authentication**: OAuth2 (JWT-based)
- **API**: JSON-based API for managing videos, users, and comments.

## Installation

1.Create and activate a virtual environment:
  python3 -m venv env
  source env/bin/activate

---------------------
2.Install dependencies:
  pip install -r requirements.txt

---------------------
3.Set up environment variables for the database and authentication:
  touch .env
  DB_HOST= your host
  DB_PORT= your port
  DB_NAME=your db_name
  DB_USER= your db_user
  DB_PASS= your db_pass
  SECRET_AUTH= your SECRET_AUTH



----------------------
4.Run database migrations:
    alembic upgrade head

5.Start the FastAPI server:  
  uvicorn main:app --reload

-----------------
Open the app in your browser at http://127.0.0.1:8000.

  
