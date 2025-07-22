# Free Hosting Deployment Guide for Notetion Public

This guide walks you through deploying your Notetion public version to free hosting platforms.

## 🚀 Option 1: Streamlit Community Cloud (Recommended)

**Best for**: Easy deployment, automatic updates, built for Streamlit apps

### Repository Requirements:
- ⚠️ **Repository must be PUBLIC** for free tier
- 💡 **Alternative**: Use GitHub Codespaces or other platforms for private repos

### Steps:

1. **Make repository public** (if it's currently private):
   - Go to your GitHub repo settings
   - Scroll to "Danger Zone"
   - Click "Change repository visibility"
   - Select "Make public"

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add public version for deployment"
   git push origin main
   ```

3. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `michaelflorip/notetion`
   - Set main file path: `streamlit_app_public.py`
   - Click "Deploy!"

4. **Your app will be live at**: `https://your-app-name.streamlit.app`

### Pros:
- ✅ **Completely free**
- ✅ **Auto-deploys on git push**
- ✅ **Built for Streamlit**
- ✅ **No configuration needed**

### Cons:
- ❌ **Repository must be PUBLIC**
- ❌ Apps sleep after inactivity
- ❌ Limited resources
- ❌ Streamlit branding

### 🔒 **Privacy Alternatives for Private Repos:**

If you want to keep your repository private, consider these options instead:

1. **Railway** - Works with private repos, $5/month free credit
2. **Render** - Supports private repos on free tier
3. **Fly.io** - Works with private repos
4. **GitHub Codespaces** - Works with private repos (60 hours/month free)

---

## 🐙 Option 2: GitHub Codespaces + Port Forwarding

**Best for**: Development and testing, temporary hosting

### Steps:

1. **Create Codespace**:
   - Go to your GitHub repo
   - Click "Code" → "Codespaces" → "Create codespace"

2. **Run the app**:
   ```bash
   pip install -r requirements_public.txt
   streamlit run streamlit_app_public.py --server.port 8501
   ```

3. **Make port public**:
   - In Codespaces, go to "Ports" tab
   - Right-click port 8501
   - Select "Port Visibility" → "Public"

### Pros:
- ✅ **Free (60 hours/month)**
- ✅ **Full control**
- ✅ **Easy setup**

### Cons:
- ❌ **Temporary** (stops when inactive)
- ❌ **Limited hours**

---

## 🔥 Option 3: Railway (Free Tier)

**Best for**: Production-like hosting with databases

### Steps:

1. **Create Railway account**: [railway.app](https://railway.app)

2. **Deploy from GitHub**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `notetion` repository

3. **Configure deployment**:
   - Railway will auto-detect Python
   - Set start command: `streamlit run streamlit_app_public.py --server.port $PORT --server.address 0.0.0.0`

4. **Set environment variables** (if needed):
   - Go to Variables tab
   - Add any required environment variables

### Pros:
- ✅ **$5/month free credit**
- ✅ **Always-on hosting**
- ✅ **Database support**
- ✅ **Custom domains**

### Cons:
- ❌ **Limited free tier**
- ❌ **Credit-based**

---

## 🌐 Option 4: Render (Free Tier)

**Best for**: Professional hosting with custom domains

### Steps:

1. **Create Render account**: [render.com](https://render.com)

2. **Create Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select `notetion` repo

3. **Configure service**:
   - **Name**: `notetion-public`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements_public.txt`
   - **Start Command**: `streamlit run streamlit_app_public.py --server.port $PORT --server.address 0.0.0.0`

4. **Deploy**: Click "Create Web Service"

### Pros:
- ✅ **Free tier available**
- ✅ **Always-on**
- ✅ **SSL certificates**
- ✅ **Custom domains**

### Cons:
- ❌ **Spins down after 15min inactivity**
- ❌ **Slower cold starts**

---

## 🐳 Option 5: Fly.io (Free Tier)

**Best for**: Docker-based deployment, global edge hosting

### Steps:

1. **Install Fly CLI**:
   ```bash
   # macOS
   brew install flyctl
   
   # Linux/Windows
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and initialize**:
   ```bash
   fly auth login
   fly launch --dockerfile Dockerfile.public
   ```

3. **Configure fly.toml** (auto-generated):
   ```toml
   app = "notetion-public"
   
   [build]
     dockerfile = "Dockerfile.public"
   
   [[services]]
     http_checks = []
     internal_port = 8501
     processes = ["app"]
     protocol = "tcp"
     script_checks = []
   
     [[services.ports]]
       force_https = true
       handlers = ["http"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

4. **Deploy**:
   ```bash
   fly deploy
   ```

### Pros:
- ✅ **Free tier** (3 shared-cpu-1x, 160GB transfer)
- ✅ **Global edge network**
- ✅ **Docker support**
- ✅ **Always-on**

### Cons:
- ❌ **More complex setup**
- ❌ **CLI required**

---

## 📋 Quick Comparison

| Platform | Free Tier | Always-On | Custom Domain | Ease of Setup |
|----------|-----------|-----------|---------------|---------------|
| **Streamlit Cloud** | ✅ Unlimited | ❌ Sleeps | ❌ No | ⭐⭐⭐⭐⭐ |
| **Railway** | ✅ $5 credit | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐ |
| **Render** | ✅ Limited | ❌ Sleeps | ✅ Yes | ⭐⭐⭐⭐ |
| **Fly.io** | ✅ Limited | ✅ Yes | ✅ Yes | ⭐⭐⭐ |
| **Codespaces** | ✅ 60h/month | ❌ Temporary | ❌ No | ⭐⭐⭐⭐ |

---

## 🎯 Recommended Approach

### For Quick Testing:
1. **Streamlit Community Cloud** - Easiest setup, perfect for demos

### For Production:
1. **Railway** - Best balance of features and reliability
2. **Fly.io** - Most robust free tier for always-on hosting

---

## 🔧 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All files are committed to GitHub
- [ ] `streamlit_app_public.py` runs locally without errors
- [ ] Requirements are up to date in `requirements_public.txt`
- [ ] No sensitive data in code (API keys, etc.)
- [ ] Database file path is writable in deployment environment

---

## 🚨 Important Notes

1. **Database Persistence**: Free tiers may not persist files between deployments. Consider using external database for production.

2. **Resource Limits**: Free tiers have CPU/memory limits. Monitor usage.

3. **Custom Domains**: Most platforms offer custom domains on free tiers.

4. **SSL**: All recommended platforms provide free SSL certificates.

5. **Monitoring**: Set up basic monitoring to track uptime and usage.

---

## 🆘 Troubleshooting

### Common Issues:

**Port binding errors**:
```python
# Make sure your app uses the PORT environment variable
port = int(os.environ.get("PORT", 8501))
```

**Module not found**:
- Ensure all dependencies are in `requirements_public.txt`
- Check Python version compatibility

**Database errors**:
- Ensure write permissions for SQLite database
- Consider using environment-specific database paths

**Memory issues**:
- Optimize file processing for large uploads
- Consider implementing file size limits

---

## 🎉 Next Steps After Deployment

1. **Test thoroughly** with different file types
2. **Monitor usage** and performance
3. **Set up analytics** (optional)
4. **Share with users** and gather feedback
5. **Consider upgrading** to paid tiers for production use

Your Notetion app is now ready for the world! 🌍
