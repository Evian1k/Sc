#!/bin/bash

echo "Fixing Node.js compatibility issues for Vite..."

# Check Node.js version
NODE_VERSION=$(node --version)
echo "Current Node.js version: $NODE_VERSION"

# If using Node.js 22+, we need to use a compatible Vite version
if [[ "$NODE_VERSION" =~ ^v2[2-9] ]]; then
    echo "Detected Node.js 22+, installing compatible Vite version..."
    npm install vite@^6.3.5 @vitejs/plugin-react@^4.7.0
else
    echo "Node.js version is compatible with latest Vite"
fi

# Clear cache
echo "Clearing npm cache..."
npm cache clean --force

# Remove node_modules and reinstall
echo "Reinstalling dependencies..."
rm -rf node_modules package-lock.json
npm install

echo "Node.js compatibility issues fixed!"
echo "You can now run: npm run dev"