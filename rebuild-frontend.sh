#!/bin/bash

# Script to rebuild and restart the frontend
echo "=== Rebuilding EduAI Frontend ==="

# Navigate to frontend directory
cd frontend

# Clean node_modules (optional)
echo "Would you like to clean the node_modules directory? (y/n)"
read -r clean_modules

if [[ $clean_modules == "y" ]]; then
  echo "Cleaning node_modules..."
  rm -rf node_modules
  rm -rf .next
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Install specific Tailwind CSS dependencies
echo "Installing Tailwind CSS and required packages..."
npm install -D tailwindcss@3.2.7 postcss@8.4.21 autoprefixer@10.4.14

# Initialize Tailwind if needed
if [ ! -f tailwind.config.js ]; then
  echo "Initializing Tailwind CSS..."
  npx tailwindcss init -p
fi

# Build the application
echo "Building the application..."
npm run build

# Start the application
echo "Starting the application..."
npm run dev

echo "Frontend restarted! Access at http://localhost:3000" 