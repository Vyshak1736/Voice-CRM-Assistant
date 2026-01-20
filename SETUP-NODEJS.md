# Node.js Setup Guide for Voice CRM PWA

## Current Status
✅ Backend server is running on http://localhost:8000  
❌ Node.js is not installed on this system  
❌ Frontend cannot be built without Node.js

## Quick Solutions

### Option 1: Install Node.js (Recommended)

#### Windows Installation
1. Download Node.js from https://nodejs.org/en/download/
2. Select the Windows Installer (.msi) for LTS version
3. Run the installer with default settings
4. Restart your terminal/command prompt
5. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

#### Alternative: Using Chocolatey
```cmd
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Node.js
choco install nodejs
```

### Option 2: Use Online React Development

#### StackBlitz (Instant Setup)
1. Visit https://stackblitz.com/
2. Create new React project
3. Copy frontend code from this repository
4. Connect to backend at http://localhost:8000

#### CodeSandbox
1. Visit https://codesandbox.io/
2. Create React sandbox
3. Upload frontend files
4. Configure API endpoint to http://localhost:8000

### Option 3: Docker Setup (Advanced)

```dockerfile
# Dockerfile for frontend
FROM node:18-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Current Working Backend

The backend server is running successfully with these endpoints:
- `GET /` - API status
- `GET /api/health` - Health check
- `POST /api/transcribe` - Audio transcription (mock)
- `POST /api/extract` - Data extraction
- `GET /api/evaluation/results` - Test results
- `POST /api/evaluation/run` - Run tests

## Next Steps

1. **Install Node.js** using one of the methods above
2. **Setup frontend**:
   ```cmd
   cd frontend
   npm install
   npm start
   ```
3. **Test the application** at http://localhost:3000

## Alternative: Static HTML Version

If Node.js installation is not possible, I can create a static HTML version that works with the existing backend API.

## Verification Commands

After Node.js installation, run these to verify:

```cmd
# Check Node.js version
node --version

# Check npm version  
npm --version

# Install frontend dependencies
cd frontend
npm install

# Start development server
npm start
```

## Troubleshooting

### Common Node.js Issues
- **"node is not recognized"**: Restart terminal after installation
- **Permission errors**: Run installer as Administrator
- **Network issues**: Use offline installer if available

### Frontend Issues
- **Port 3000 in use**: Kill existing processes or change port
- **CORS errors**: Backend allows localhost:3000 by default
- **API connection**: Ensure backend is running on port 8000

## Production Deployment

Once Node.js is installed, you can build for production:

```cmd
cd frontend
npm run build
```

This creates an optimized build in the `build/` folder that can be deployed to any static hosting service.
