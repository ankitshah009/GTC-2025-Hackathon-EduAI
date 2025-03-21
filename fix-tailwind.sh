#!/bin/bash

# Script to fix Tailwind CSS issues
echo "=== Fixing Tailwind CSS for EduAI Frontend ==="

# Navigate to frontend directory
cd frontend

# Clean out node_modules and build caches
echo "Cleaning node_modules and build caches..."
rm -rf node_modules
rm -rf .next
rm -rf package-lock.json

# Ensure required directories exist
mkdir -p public

# Install specific versions of packages known to work well together
echo "Installing dependencies with specific versions..."
npm install next@13.2.4 react@18.2.0 react-dom@18.2.0 axios@1.3.4 react-markdown@8.0.5

# Install Tailwind CSS and related packages with specific versions
echo "Installing Tailwind CSS with specific versions..."
npm install -D tailwindcss@3.2.7 postcss@8.4.21 autoprefixer@10.4.14

# Generate fresh Tailwind config
echo "Generating fresh Tailwind configuration..."
npx tailwindcss init -p

# Create a new CSS file to ensure it gets processed correctly
echo "Updating globals.css file..."
cat > styles/globals.css << EOF
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-rgb: 255, 255, 255;
  --primary-color: #5e35b1;
  --secondary-color: #7e57c2;
}

html,
body {
  padding: 0;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen,
    Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
}

* {
  box-sizing: border-box;
}
EOF

# Build the application
echo "Building the application..."
npm run build

# Start the application
echo "Starting the application..."
npm run dev

echo "Tailwind CSS should now be working properly! Access the app at http://localhost:3000" 