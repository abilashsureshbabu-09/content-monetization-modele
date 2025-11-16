# Deployment Guide for YouTube Revenue Predictor

## Option 1: Streamlit Cloud (EASIEST - Recommended)

### Steps:
1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/content-monetization-modeler.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Connect your GitHub repository
   - Select the branch and file: `app/streamlit_app.py`
   - Click "Deploy"

3. **Add Secrets**
   - In Streamlit Cloud dashboard, go to Settings → Secrets
   - Add your YouTube API key:
     ```
     YT_API_KEY = "AIzaSyBn526TaNxHvRw13e6eAUHEBXHi2gI6uGc"
     ```
   - The app will automatically restart

**Pros:** Free tier available, auto-deploys from GitHub, easiest setup
**Cons:** Free tier has limitations on runtime hours

---

## Option 2: Heroku (Free tier ended, but still affordable)

### Steps:
1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set secrets: `heroku config:set YT_API_KEY=AIzaSyBn526TaNxHvRw13e6eAUHEBXHi2gI6uGc`
5. Deploy: `git push heroku main`

**Pros:** Simple deployment, good documentation
**Cons:** No free tier anymore (starts at ~$7/month)

---

## Option 3: Railway.app (Modern Alternative)

### Steps:
1. Go to https://railway.app
2. Create account and link GitHub
3. Create new project → Deploy from GitHub
4. Select repository
5. Add environment variables in Settings
6. Deploy

**Pros:** Generous free tier, easy setup
**Cons:** Free tier credit limits

---

## Option 4: PythonAnywhere (Traditional Python Hosting)

### Steps:
1. Go to https://www.pythonanywhere.com
2. Create free account
3. Upload files via web interface or git
4. Set up Streamlit as web app
5. Configure domain

**Pros:** Python-specific hosting, good for Python projects
**Cons:** Steeper learning curve

---

## Option 5: Google Cloud Run (Scalable)

### Steps:
1. Create `app.yaml`:
   ```yaml
   runtime: python311
   env: standard
   ```

2. Create `cloudbuild.yaml`

3. Deploy:
   ```bash
   gcloud run deploy content-monetization --source .
   ```

**Pros:** Highly scalable, production-grade
**Cons:** More complex setup, can be expensive

---

## RECOMMENDED: Use Streamlit Cloud

**Why?**
- ✅ Completely free for public projects
- ✅ Automatic deployment from GitHub
- ✅ Perfect for Streamlit apps
- ✅ Built-in secret management
- ✅ One-click setup

**Quick Start:**
1. Push this repo to GitHub
2. Go to https://streamlit.io/cloud
3. Click "New app" → Select GitHub repo
4. Select file: `app/streamlit_app.py`
5. Go to Settings → Secrets → Add YouTube API key
6. Done! App is live 🚀

---

## Environment Variables Needed

For any platform, ensure these are set:
- `YT_API_KEY` = Your YouTube Data API v3 key
- `MODEL_PATH` = Path to model (usually `models/best_model.joblib`)

---

## Files Ready for Deployment

✅ `requirements.txt` - All dependencies
✅ `Procfile` - For Heroku
✅ `.streamlit/config.toml` - Streamlit configuration
✅ `.streamlit/secrets.toml` - Secrets template
✅ `app/streamlit_app.py` - Main app
✅ `src/` - All modules
✅ `models/best_model.joblib` - Pre-trained model

---

## Post-Deployment Testing

Once deployed, test:
1. Visit your app URL
2. Use "Manual Entry" tab to test predictions
3. Use "Fetch via YouTube URL" tab with a video URL
4. Verify revenue predictions are working

---

## Need Help?

- Streamlit Docs: https://docs.streamlit.io
- Streamlit Cloud: https://streamlit.io/cloud
- YouTube API: https://developers.google.com/youtube/v3

You're ready to go! 🎉
