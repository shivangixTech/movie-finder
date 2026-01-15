import os
import json
import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build  # START: New Import for YouTube API

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="AI Movie Recommender",
    layout="centered"
)

st.title("🎬 AI Movie Recommender")
st.write("Tell me your mood and preferences. I’ll suggest movies with real trailers.")

# ---------------- API Keys ----------------

# 1. Gemini API Key
api_key = 'AIzaSyBu289VNNqcRP33sNU6SqHpQTpFKq3Ssns'

if not api_key or api_key == "PASTE_YOUR_API_KEY_HERE":
    st.error("Gemini API key not found.")
    st.stop()

genai.configure(api_key=api_key)

# 2. YouTube API Key
YOUTUBE_API_KEY = 'AIzaSyDkG2F6HAEr0J5yq7J8y6SPaJRcb33e6Wk'
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# ---------------- Helper Function: Get YouTube Trailer ----------------
def get_trailer_url(movie_title, release_year):
    try:
        query = f"{movie_title} {release_year} official trailer"
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=1
        )
        response = request.execute()
        
        if response['items']:
            video_id = response['items'][0]['id']['videoId']
            return f"https://www.youtube.com/watch?v={video_id}"
        return "https://www.youtube.com"
    except Exception:
        return None

# ---------------- User Inputs ----------------
genre = st.text_input("Genre (e.g. Thriller, Romance, Sci-Fi)")

mood = st.selectbox(
    "Mood",
    ["Relaxed", "Intense", "Emotional", "Fun"]
)

pace = st.selectbox(
    "Movie pace",
    ["Fast-paced", "Slow and calm"]
)

complexity = st.selectbox(
    "Story complexity",
    ["Simple", "Medium", "Mind-bending"]
)

avoid = st.text_input("Genres or themes to avoid (optional)")

duration = st.selectbox(
    "Available time",
    ["Under 90 minutes", "Around 2 hours", "More than 2 hours"]
)

platform = st.selectbox(
    "Preferred OTT platform",
    ["Netflix", "Amazon Prime", "Disney+ Hotstar", "Any"]
)

favorites = st.text_input("Movies you already like (optional)")

# ---------------- Button Action ----------------
if st.button(" Recommend Movies"):
    if not genre:
        st.warning("Genre is required.")
    else:
        prompt = f"""
        You are a professional movie recommendation expert.

        TASK:
        Recommend EXACTLY 10 movies based on these preferences:
        Genre: {genre}
        Mood: {mood}
        Pace: {pace}
        Story Complexity: {complexity}
        Avoid: {avoid}
        Time Available: {duration}
        Preferred Platform: {platform}
        Liked Movies: {favorites}

        RULES:
        - Return EXACTLY 10 movies (not less, not more)
        - Each movie must be unique
        - Prefer well-rated and popular movies

        OUTPUT FORMAT (STRICT JSON ONLY):
        Return a raw JSON list of objects.
        No markdown, no explanations, no text outside JSON.

        Structure:
        [
            {{
                "title": "Movie Title",
                "year": "Release Year",
                "rating": "IMDb Rating",
                "reason": "Short one-line reason"
            }}
        ]
        """

        with st.spinner("Generating recommendations and fetching trailers..."):
            try:
                model = genai.GenerativeModel("gemini-3-flash-preview")
                response = model.generate_content(prompt)

                clean_text = response.text.strip().replace("```json", "").replace("```", "")
                movies = json.loads(clean_text)

                st.subheader("🎬 Recommended Movies")

                for idx, movie in enumerate(movies, 1):
                    trailer_link = get_trailer_url(movie['title'], movie['year'])

                    with st.container():
                        st.markdown(f"### {idx}. {movie['title']} ({movie['year']})")
                        st.write(f"**IMDb:** {movie['rating']} ⭐")
                        st.write(f"_{movie['reason']}_")

                        if trailer_link:
                            st.markdown(f"[ Watch Trailer on YouTube]({trailer_link})")
                        else:
                            st.write("Trailer not found.")

                        st.divider()

            except json.JSONDecodeError:
                st.error("Error parsing AI response. Please try again.")
            except Exception as e:
                st.error("An error occurred")
                st.write(e)
