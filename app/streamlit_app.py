
# app/streamlit_app.py (updated with YouTube URL fetch)
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import sys

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processing import feature_engineering
from src.youtube_fetch import extract_video_id, fetch_video_metadata, fetch_channel_subscribers, build_feature_row_from_video, fetch_category_map

st.set_page_config(page_title='YouTube Revenue Predictor', layout='centered')
st.title('YouTube Ad Revenue Predictor')
st.markdown('Predict YouTube ad revenue from video metadata. You can either fetch data via YouTube URL (requires API key) or enter metrics manually.')

MODEL_PATH = os.environ.get('MODEL_PATH', 'models/best_model.joblib')
YT_API_KEY = os.environ.get('YT_API_KEY')

@st.cache_data
def load_model_bundle(path):
    try:
        return joblib.load(path)
    except FileNotFoundError:
        st.warning(f"⚠️ Model file not found at {path}. Please train the model first by running: python notebook.py")
        return None
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

@st.cache_data
def load_category_map(api_key):
    try:
        return fetch_category_map(api_key=api_key)
    except Exception:
        return {}

st.sidebar.header('Configuration')
retention_rate = st.sidebar.slider('Estimated average retention (fraction of video watched)', min_value=0.05, max_value=0.9, value=0.30, step=0.05)
model_path_input = st.sidebar.text_input('Model path (optional)', value=MODEL_PATH)

tab1, tab2 = st.tabs(['Fetch via YouTube URL', 'Manual Entry'])

with tab1:
    st.subheader('Fetch & Predict from YouTube')
    if not YT_API_KEY:
        st.warning('⚠️ No YouTube API key detected. To use this feature, set the YT_API_KEY environment variable.')
    
    col1, col2 = st.columns([3,1])
    with col1:
        video_url = st.text_input('YouTube video URL or ID', placeholder='https://www.youtube.com/watch?v=XXXXXXXXXXX', key='url_input')
    with col2:
        fetch_button = st.button('Fetch & Predict', key='fetch_btn')

    if fetch_button:
        vid = extract_video_id(video_url)
        if not vid:
            st.error('Could not extract a video id from that input. Paste a full YouTube URL or the 11-char id.')
            st.stop()

        try:
            bundle = load_model_bundle(model_path_input)
        except Exception as e:
            st.error(f'Failed to load model bundle at {model_path_input}: {e}')
            st.stop()

        model = bundle.get('model')
        artifacts = bundle.get('artifacts')
        if model is None or artifacts is None:
            st.error('Model bundle appears incomplete (needs "model" and "artifacts").')
            st.stop()

        try:
            video_meta = fetch_video_metadata(vid, api_key=YT_API_KEY)
            if video_meta is None:
                st.error('No metadata returned for the video id (video may not exist or may be private).')
                st.stop()

            subs = None
            if video_meta.get('channelId'):
                try:
                    subs = fetch_channel_subscribers(video_meta['channelId'], api_key=YT_API_KEY)
                except Exception:
                    subs = None

            cat_map = load_category_map(YT_API_KEY)
            feature_row = build_feature_row_from_video(video_meta, retention_rate=retention_rate, category_map=cat_map)
            feature_row['subscribers'] = subs or 0

        except Exception as e:
            st.error(f'Failed to fetch video metadata: {e}')
            st.stop()

        st.markdown('### Fetched metadata (public)')
        md = {
            'Video ID': feature_row.get('video_id'),
            'Title': video_meta.get('title'),
            'Published': video_meta.get('publishedAt'),
            'Views': feature_row.get('views'),
            'Likes': feature_row.get('likes'),
            'Comments': feature_row.get('comments'),
            'Duration (min)': feature_row.get('video_length_minutes'),
            'Channel subscribers': feature_row.get('subscribers'),
        }
        st.json(md)

        X_row = pd.DataFrame([{
            'views': feature_row['views'],
            'likes': feature_row['likes'],
            'comments': feature_row['comments'],
            'watch_time_minutes': feature_row['watch_time_minutes'],
            'video_length_minutes': feature_row['video_length_minutes'],
            'subscribers': feature_row['subscribers'],
            'category': feature_row['category'],
            'device': feature_row['device'],
            'country': feature_row['country'],
            'date': pd.to_datetime(feature_row.get('publishedAt')) if feature_row.get('publishedAt') else pd.to_datetime('today')
        }])

        X_row = feature_engineering(X_row)

        feat_cols = artifacts['feature_columns']
        X_feat = pd.DataFrame(0, index=[0], columns=feat_cols)

        for col in X_row.select_dtypes(include=[np.number]).columns:
            if col in X_feat.columns:
                X_feat.loc[0, col] = X_row.loc[0, col]

        for cat in ['category', 'device', 'country']:
            val = X_row.loc[0].get(cat)
            if pd.isna(val):
                continue
            candidates = [c for c in feat_cols if c.startswith(cat + '_')]
            for cand in candidates:
                if str(val) in cand or cand.endswith(f"_{val}"):
                    X_feat.loc[0, cand] = 1

        try:
            pred = model.predict(X_feat)[0]
            st.success(f"Estimated ad revenue (USD): ${pred:,.2f}")
            st.write("Note: this is an estimate from a learner model — refine with better watch_time and retention data for improved accuracy.")
        except Exception as e:
            st.error(f'Prediction failed: {e}')
            st.write('Model expected features:', feat_cols[:20], '...')

with tab2:
    st.subheader('Manual Metrics Entry')
    st.markdown('Enter video metrics manually without needing a YouTube API key.')
    
    col1, col2 = st.columns(2)
    with col1:
        views = st.number_input('Views', min_value=0, value=1000)
        likes = st.number_input('Likes', min_value=0, value=50)
        comments = st.number_input('Comments', min_value=0, value=20)
        video_length_min = st.number_input('Video length (minutes)', min_value=0.1, value=10.0)
    with col2:
        subscribers = st.number_input('Channel subscribers', min_value=0, value=10000)
        category = st.selectbox('Category', options=['Gaming', 'Music', 'Education', 'Entertainment', 'Sports', 'Other'])
        device = st.selectbox('Primary device', options=['Mobile', 'Desktop', 'Tablet', 'Smart TV'])
        country = st.selectbox('Country', options=['US', 'IN', 'BR', 'GB', 'JP', 'Other'])
    
    watch_time_min = video_length_min * retention_rate
    
    if st.button('Predict', key='manual_btn'):
        try:
            bundle = load_model_bundle(model_path_input)
        except Exception as e:
            st.error(f'Failed to load model bundle at {model_path_input}: {e}')
            st.stop()

        model = bundle.get('model')
        artifacts = bundle.get('artifacts')
        if model is None or artifacts is None:
            st.error('Model bundle appears incomplete (needs "model" and "artifacts").')
            st.stop()

        X_row = pd.DataFrame([{
            'views': views,
            'likes': likes,
            'comments': comments,
            'watch_time_minutes': watch_time_min,
            'video_length_minutes': video_length_min,
            'subscribers': subscribers,
            'category': category,
            'device': device,
            'country': country,
            'date': pd.to_datetime('today')
        }])

        X_row = feature_engineering(X_row)

        feat_cols = artifacts['feature_columns']
        X_feat = pd.DataFrame(0, index=[0], columns=feat_cols)

        for col in X_row.select_dtypes(include=[np.number]).columns:
            if col in X_feat.columns:
                X_feat.loc[0, col] = X_row.loc[0, col]

        for cat in ['category', 'device', 'country']:
            val = X_row.loc[0].get(cat)
            if pd.isna(val):
                continue
            candidates = [c for c in feat_cols if c.startswith(cat + '_')]
            for cand in candidates:
                if str(val) in cand or cand.endswith(f"_{val}"):
                    X_feat.loc[0, cand] = 1

        try:
            pred = model.predict(X_feat)[0]
            st.success(f"Estimated ad revenue (USD): ${pred:,.2f}")
            st.write("**Input metrics:**")
            st.json({
                'Views': views,
                'Likes': likes,
                'Comments': comments,
                'Watch time (min)': round(watch_time_min, 2),
                'Video length (min)': video_length_min,
                'Subscribers': subscribers,
                'Category': category,
                'Device': device,
                'Country': country,
                'Retention rate': retention_rate
            })
        except Exception as e:
            st.error(f'Prediction failed: {e}')
            st.write('Model expected features:', feat_cols[:20], '...')

st.markdown('---')
st.markdown('**Note:** For better predictions, use actual watch-time data and retention metrics from YouTube Analytics if available.')
