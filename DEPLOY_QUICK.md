# Quick Deployment Steps

## Fastest Way to Host (Streamlit Cloud - FREE)

### 1. Push to GitHub
```bash
cd /Users/abilashsureshbabu/Downloads/Content_Monetization_Modeler_updated
git init
git add .
git commit -m "YouTube Revenue Predictor"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/content-monetization-modeler.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud
- Visit: https://streamlit.io/cloud
- Click: "New app"
- Select your GitHub repository
- Branch: `main`
- File path: `app/streamlit_app.py`
- Click: "Deploy"

### 3. Add YouTube API Key (in Streamlit Cloud)
- Go to your app in Streamlit Cloud
- Click: ⚙️ Settings (bottom right)
- Click: "Secrets"
- Add:
  ```
  YT_API_KEY = "AIzaSyBn526TaNxHvRw13e6eAUHEBXHi2gI6uGc"
  ```
- Save and app auto-restarts

### 4. Done! 🎉
Your app is now live at:
```
https://[your-username]-content-monetization-modeler.streamlit.app
```

---

## Alternative Quick Options

### Railway.app (Also Free with Limits)
1. Go to https://railway.app
2. "New Project" → "Deploy from GitHub"
3. Connect your repo
4. Add environment: `YT_API_KEY=...`
5. Deploy

### Heroku (Paid, ~$7/month)
```bash
heroku create your-app-name
heroku config:set YT_API_KEY="AIzaSyBn526TaNxHvRw13e6eAUHEBXHi2gI6uGc"
git push heroku main
```

---

## Files Already Prepared
✅ `requirements.txt` - Dependencies
✅ `Procfile` - Heroku config
✅ `.streamlit/secrets.toml` - Secrets template
✅ `app/streamlit_app.py` - Main app
✅ `models/best_model.joblib` - Model included

**You're ready to deploy!** 🚀
