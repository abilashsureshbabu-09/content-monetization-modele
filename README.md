
# Content Monetization Modeler (Updated)

This project predicts YouTube ad revenue from video metadata using regression models and provides a Streamlit app that can accept a YouTube URL to fetch public metadata and estimate revenue.

## New features in this update
- `src/youtube_fetch.py`: utilities to extract video id from URL, fetch public video metadata and channel subscribers via YouTube Data API v3, simple caching, and feature row builder.
- Updated `app/streamlit_app.py` to support "Fetch & Predict" from a YouTube URL (requires YouTube API key).
- `requirements.txt` now includes `requests` and `isodate`.
- Simple local cache for API results in `data/yt_cache.json`.

## Important: YouTube API Key
- Create a key in Google Cloud Console and enable YouTube Data API v3.
- Export it to your environment before running Streamlit:
  ```bash
  export YT_API_KEY='YOUR_KEY'
  streamlit run app/streamlit_app.py
  ```
- Or add it to Streamlit secrets.

## How it works
1. Train your model using `python notebook.py --data data/youtube_monetization.csv` which will produce `models/best_model.joblib`.
2. Run Streamlit. Paste a YouTube URL, click **Fetch & Predict**.
3. The app fetches public metadata (views, likes, comments, duration), estimates `watch_time_minutes` using a configurable retention rate, aligns features to the trained model and predicts ad revenue.

## Tips to improve estimates
- Use channel-level metrics and real watch-time from YouTube Analytics (requires OAuth).
- Map categoryId to readable categories (the app uses categories API).
- Tune retention rate based on your historical data.
- Consider training on a log-transformed target (`log1p`) if revenue distribution is skewed.
