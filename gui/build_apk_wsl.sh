#!/bin/bash

# Research Data Collector - APK Builder for WSL
# Run this script in WSL Ubuntu

echo "=== Research Data Collector APK Builder ==="
echo "This script will build your Android APK using Buildozer"
echo ""

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required dependencies
echo "Installing build dependencies..."
sudo apt-get install -y python3-pip build-essential git python3 python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

# Install Java
echo "Installing Java..."
sudo apt-get install -y openjdk-8-jdk

# Install additional dependencies
echo "Installing additional dependencies..."
sudo apt-get install -y autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# Install buildozer
echo "Installing Buildozer..."
pip3 install buildozer

# Install Android SDK dependencies
echo "Installing Android SDK dependencies..."
sudo apt-get install -y libltdl-dev libffi-dev libssl-dev

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found in current directory"
    echo "Please run this script from the gui directory"
    exit 1
fi

if [ ! -f "buildozer.spec" ]; then
    echo "Error: buildozer.spec not found in current directory"
    echo "Please run this script from the gui directory"
    exit 1
fi

echo "Starting APK build..."
echo "This will take 10-15 minutes..."

# Build the APK
buildozer android debug

# Check if build was successful
if [ -f "bin/*.apk" ]; then
    echo ""
    echo "=== BUILD SUCCESSFUL! ==="
    echo "APK file created in bin/ directory"
    ls -la bin/
    echo ""
    echo "You can now copy the APK file to your Windows system:"
    echo "cp bin/*.apk /mnt/c/Users/Windows/Desktop/"
else
    echo ""
    echo "=== BUILD FAILED ==="
    echo "Check the buildozer.log file for errors"
    echo "Common issues:"
    echo "1. Missing dependencies"
    echo "2. Network connectivity issues"
    echo "3. Insufficient disk space"
    echo "4. Memory issues"
fi
