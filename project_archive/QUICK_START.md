# 🚀 GödelOS Quick Start Guide

**Get GödelOS v0.2 Beta running in minutes with Svelte or HTML frontend!**

## ⚡ One-Command Start

```bash
# First-time setup and start (auto-detects best frontend)
./start-godelos.sh --setup

# Or just start (if already set up)
./start-godelos.sh
```

## 🎯 Quick Commands

| Command | Description |
|---------|-------------|
| `./start-godelos.sh` | Start with auto-detected frontend |
| `./start-godelos.sh --setup` | Install dependencies and start |
| `./start-godelos.sh --svelte-frontend` | Use modern Svelte UI |
| `./start-godelos.sh --html-frontend` | Use simple HTML UI |
| `./start-godelos.sh --dev` | Development mode (auto-reload) |
| `./start-godelos.sh --status` | Check system status |
| `./start-godelos.sh --logs` | View recent logs |
| `./stop-godelos.sh` | Stop all services |

## 🌐 Access Points

Once started, access GödelOS at:

- **🎨 Frontend UI**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🔌 WebSocket**: ws://localhost:8000/ws/cognitive-stream

## 🎨 Frontend Options

GödelOS supports two frontend implementations:

### 🚀 **Svelte Frontend** (Recommended)
- **Modern reactive UI** with component-based architecture
- **Real-time visualizations** with D3.js integration
- **Advanced features** like cognitive transparency monitoring
- **Auto-detected** when Node.js and npm are available

```bash
# Force Svelte frontend
./start-godelos.sh --svelte-frontend --dev
```

### 📄 **HTML Frontend** (Fallback)
- **Simple static files** served with Python HTTP server
- **No build step required** - works without Node.js
- **Basic functionality** for core interactions
- **Automatic fallback** when Svelte dependencies unavailable

```bash
# Force HTML frontend  
./start-godelos.sh --html-frontend
```

## 📋 Requirements

### Core Requirements
- **Python 3.8+** (required)
- **4GB RAM** (recommended)
- **1GB disk space** (for dependencies and storage)

### For Svelte Frontend (Optional but Recommended)
- **Node.js 16+** (for modern UI features)
- **npm** (comes with Node.js)

## 🛠️ Advanced Usage

### Development Mode with Svelte
```bash
# Auto-reload for both backend and frontend
./start-godelos.sh --dev --svelte-frontend
```

### Custom Ports
```bash
# Use custom ports
GODELOS_BACKEND_PORT=8080 GODELOS_FRONTEND_PORT=3001 ./start-godelos.sh
```

### Frontend-Only Development
```bash
# For UI development with Svelte hot reload
./start-godelos.sh --frontend-only --svelte-frontend --dev
```

### Backend-Only Development
```bash
# For API development
./start-godelos.sh --backend-only --debug
```

## 🔧 First-Time Setup

### Automatic Setup (Recommended)
```bash
# Installs all dependencies and starts system
./start-godelos.sh --setup
```

### Manual Setup
```bash
# Backend dependencies
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Svelte frontend dependencies (optional)
cd ../svelte-frontend
npm install

# Start system
cd ..
./start-godelos.sh
```

## 🔧 Troubleshooting

### Check System Status
```bash
./start-godelos.sh --status
```

### View Logs
```bash
./start-godelos.sh --logs

# Or follow live logs
tail -f logs/backend.log
tail -f logs/frontend.log
```

### Clean Restart
```bash
./stop-godelos.sh
./start-godelos.sh --setup
```

### Port Conflicts
```bash
# Check what's using ports
lsof -i :8000  # Backend port
lsof -i :3000  # Frontend port

# Or use custom ports
GODELOS_BACKEND_PORT=8080 ./start-godelos.sh
```

### Node.js/npm Issues
```bash
# Check Node.js installation
node --version
npm --version

# If not installed, frontend will fallback to HTML automatically
# Or install Node.js from: https://nodejs.org/
```

## 🎯 First Steps After Starting

1. **Open Frontend**: http://localhost:3000
2. **Try a Query**: "What is artificial intelligence?"
3. **Explore API**: http://localhost:8000/docs
4. **Monitor System**: Watch the real-time cognitive transparency
5. **Check Frontend Type**: Look for "svelte" or "html" in status output

## 📖 Full Documentation

- **[Complete README](README.md)** - Detailed system documentation
- **[Integration Summary](INTEGRATION_SUMMARY.md)** - Technical integration details
- **[Test Report](test_output/beta_0.2_test_report.md)** - Current test status

## 🆘 Need Help?

1. **Check Status**: `./start-godelos.sh --status`
2. **View Logs**: `./start-godelos.sh --logs`
3. **Clean Restart**: `./stop-godelos.sh && ./start-godelos.sh --setup`
4. **System Check**: `./start-godelos.sh --check`
5. **Force Frontend**: Use `--svelte-frontend` or `--html-frontend` flags

## 🎨 Frontend Comparison

| Feature | Svelte Frontend | HTML Frontend |
|---------|----------------|---------------|
| **Setup** | Requires Node.js | Python only |
| **Performance** | Fast, reactive | Simple, lightweight |
| **Features** | Full cognitive visualization | Basic interactions |
| **Development** | Hot reload, dev tools | Static file serving |
| **Maintenance** | Modern web stack | Minimal dependencies |

---

**🧠 Welcome to GödelOS - Now with Multiple Frontend Options!**

Choose the frontend that best fits your setup and requirements. The system will auto-detect and use the best available option automatically.