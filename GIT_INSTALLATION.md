# Git Installation Guide for Windows

## 📥 Installing Git

Git is required to deploy to Railway. Follow these steps:

### Step 1: Download Git

1. **Download Link**: [git-scm.com/download/win](https://git-scm.com/download/win)
2. The download should start automatically
3. If not, click "Click here to download manually"

### Step 2: Install Git

1. Run the downloaded installer (`Git-2.xx.x-64-bit.exe`)
2. **Recommended Settings**:
   - ✅ Use default installation directory
   - ✅ Select "Git from the command line and also from 3rd-party software"
   - ✅ Use the OpenSSL library
   - ✅ Checkout Windows-style, commit Unix-style line endings
   - ✅ Use MinTTY (default terminal)
   - ✅ Default (fast-forward or merge)
   - ✅ Git Credential Manager
   - ✅ Enable file system caching

3. Click **Next** through the installer
4. Click **Install**
5. Click **Finish**

### Step 3: Verify Installation

1. **Close and reopen PowerShell** (important!)
2. Run this command:
   ```powershell
   git --version
   ```
3. You should see: `git version 2.xx.x`

---

## 🚀 After Git Installation

Once Git is installed, return here and we'll continue with Railway deployment:

### Quick Commands to Run

```powershell
# Navigate to your project
cd "C:\Users\Khalamullah\Desktop\IOT DASHBOARD"

# Initialize git repository
git init

# Configure git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - IoT Dashboard for Railway"
```

Then proceed with creating a GitHub repository and deploying to Railway as outlined in the Railway deployment guide.

---

## 🔄 Alternative: Deploy Without Git (Railway CLI)

If you prefer not to use Git, you can use Railway CLI:

### Install Railway CLI

```powershell
# Using npm (if you have Node.js installed)
npm install -g @railway/cli

# Then login and deploy
railway login
railway init
railway up
```

However, **using Git + GitHub is recommended** as it provides:

- Version control
- Easy updates
- Automatic deployments
- Better collaboration

---

## ✅ Next Steps

1. Install Git using the link above
2. Restart PowerShell
3. Run the git commands to initialize your repository
4. Create a GitHub repository
5. Push your code to GitHub
6. Deploy to Railway

See the full Railway deployment guide for detailed instructions!
