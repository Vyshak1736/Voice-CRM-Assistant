#!/bin/bash

# Voice CRM PWA to APK Builder
# This script converts the PWA to an Android APK using Trusted Web Activity

set -e

echo "🚀 Building Voice CRM PWA APK..."

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo "❌ npm is not installed. Please install npm first."
        exit 1
    fi
    
    # Check if Java is installed
    if ! command -v java &> /dev/null; then
        echo "❌ Java is not installed. Please install Java 8 or higher."
        exit 1
    fi
    
    # Check if Android SDK is installed
    if [ -z "$ANDROID_HOME" ]; then
        echo "⚠️  ANDROID_HOME is not set. Please set Android SDK path."
        echo "   Example: export ANDROID_HOME=/Users/username/Library/Android/sdk"
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Install Bubblewrap CLI for PWA to APK conversion
install_bubblewrap() {
    echo "📦 Installing Bubblewrap CLI..."
    
    if ! command -v bubblewrap &> /dev/null; then
        npm install -g @bubblewrap/cli
        echo "✅ Bubblewrap CLI installed"
    else
        echo "✅ Bubblewrap CLI already installed"
    fi
}

# Build the React frontend
build_frontend() {
    echo "🔨 Building React frontend..."
    
    cd ../frontend
    npm install
    npm run build
    
    echo "✅ Frontend built successfully"
    cd ../apk-generator
}

# Initialize Bubblewrap project
init_bubblewrap() {
    echo "🎯 Initializing Bubblewrap project..."
    
    # Remove existing project if it exists
    if [ -d "voice-crm-twa" ]; then
        rm -rf voice-crm-twa
    fi
    
    # Initialize new TWA project
    bubblewrap init \
        --manifest=../frontend/build/manifest.json \
        --directory=voice-crm-twa
    
    echo "✅ Bubblewrap project initialized"
}

# Configure the TWA project
configure_twa() {
    echo "⚙️  Configuring TWA project..."
    
    cd voice-crm-twa
    
    # Update app name and package name
    sed -i '' 's/com.example.twa/com.voice.crm.app/g' app/build.gradle
    sed -i '' 's/TWA App/Voice CRM Assistant/g' app/src/main/res/values/strings.xml
    
    # Enable fullscreen and orientation
    sed -i '' 's/android:theme="@style/Theme.AppCompat.Light.NoActionBar"/android:theme="@style/Theme.AppCompat.Light.NoActionBar"\n        android:screenOrientation="portrait"/g' app/src/main/AndroidManifest.xml
    
    # Add network security config for HTTP
    cat > app/src/main/res/xml/network_security_config.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">localhost</domain>
        <domain includeSubdomains="true">127.0.0.1</domain>
    </domain-config>
</network-security-config>
EOF
    
    # Update AndroidManifest.xml to use network security config
    sed -i '' 's/android:networkSecurityConfig="@xml/network_security_config"//g' app/src/main/AndroidManifest.xml
    sed -i '' 's/<application/<application android:networkSecurityConfig="@xml\/network_security_config"/g' app/src/main/AndroidManifest.xml
    
    cd ..
    
    echo "✅ TWA project configured"
}

# Build the APK
build_apk() {
    echo "🏗️  Building APK..."
    
    cd voice-crm-twa
    
    # Build debug APK
    bubblewrap build
    
    cd ..
    
    echo "✅ APK built successfully"
}

# Sign the APK (for release)
sign_apk() {
    echo "✍️  Signing APK..."
    
    cd voice-crm-twa
    
    # Generate keystore if it doesn't exist
    if [ ! -f "voice-crm.keystore" ]; then
        keytool -genkey -v -keystore voice-crm.keystore -alias voice-crm -keyalg RSA -keysize 2048 -validity 10000 \
            -dname "CN=Voice CRM, OU=Development, O=Voice CRM, L=City, ST=State, C=US" \
            -storepass voicecrm123 -keypass voicecrm123
    fi
    
    # Sign the APK
    jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore voice-crm.keystore \
        -storepass voicecrm123 -keypass voicecrm123 app/build/outputs/apk/debug/app-debug.apk voice-crm
    
    cd ..
    
    echo "✅ APK signed successfully"
}

# Create output directory and copy APK
create_output() {
    echo "📁 Creating output..."
    
    mkdir -p output
    
    # Copy APK to output directory
    cp voice-crm-twa/app/build/outputs/apk/debug/app-debug.apk output/VoiceCRM-Debug.apk
    
    # Create info file
    cat > output/README.txt << EOF
Voice CRM PWA APK
==================

Generated: $(date)
Package: com.voice.crm.app
Version: 1.0.0

Installation Instructions:
1. Enable "Install from unknown sources" on your Android device
2. Transfer VoiceCRM-Debug.apk to your device
3. Tap on the APK file to install
4. Grant necessary permissions (microphone, storage)

Features:
- Voice recording and transcription
- Structured data extraction
- Offline support
- PWA capabilities

Technical Details:
- Built with React PWA
- Converted to APK using Trusted Web Activity
- Backend API integration
- SQLite database for local storage

For support and documentation, visit the project repository.
EOF
    
    echo "✅ Output created in ./output directory"
}

# Main execution
main() {
    echo "🎉 Starting Voice CRM APK build process..."
    
    check_prerequisites
    install_bubblewrap
    build_frontend
    init_bubblewrap
    configure_twa
    build_apk
    sign_apk
    create_output
    
    echo ""
    echo "🎊 Build completed successfully!"
    echo "📱 APK Location: ./output/VoiceCRM-Debug.apk"
    echo "📋 Installation instructions: ./output/README.txt"
    echo ""
    echo "Next steps:"
    echo "1. Transfer the APK to your Android device"
    echo "2. Enable 'Install from unknown sources' in device settings"
    echo "3. Install the APK"
    echo "4. Launch the Voice CRM app"
    echo ""
}

# Run main function
main "$@"
