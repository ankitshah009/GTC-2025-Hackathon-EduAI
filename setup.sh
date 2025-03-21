#!/bin/bash

# EduAI Setup Script
# This script sets up and tests the EduAI application (both backend and frontend)

# Print colorful messages
print_message() {
  echo -e "\033[1;34m>>> $1\033[0m"
}

print_success() {
  echo -e "\033[1;32m>>> $1\033[0m"
}

print_error() {
  echo -e "\033[1;31m>>> ERROR: $1\033[0m"
}

print_section() {
  echo -e "\n\033[1;35m=== $1 ===\033[0m"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
  print_error "Python 3 is not installed. Please install Python 3 first."
  exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
  print_error "Node.js is not installed. Please install Node.js first."
  exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
  print_error "npm is not installed. Please install npm first."
  exit 1
fi

print_section "SETUP MODE SELECTION"
echo "1) Development mode (local setup)"
echo "2) Docker mode"
read -p "Select setup mode [1/2]: " setup_mode

case $setup_mode in
  1)
    # Development mode setup
    dev_mode=true
    print_message "Setting up in development mode..."
    ;;
  2)
    # Docker mode setup
    dev_mode=false
    print_message "Setting up in Docker mode..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
      print_error "Docker is not installed. Please install Docker first."
      exit 1
    fi

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
      print_error "Docker Compose is not installed. Please install Docker Compose first."
      exit 1
    fi
    ;;
  *)
    print_error "Invalid option. Exiting."
    exit 1
    ;;
esac

# Create necessary environment files
print_section "ENVIRONMENT SETUP"

# Backend .env setup
if [ ! -f backend/.env ]; then
  print_message "Creating backend environment file..."
  if [ -f backend/.env.example ]; then
    cp backend/.env.example backend/.env
  else
    cat > backend/.env << EOF
# App settings
APP_NAME=EduAI
APP_DESCRIPTION=AI-Powered Educational Content Generator
APP_VERSION=1.0.0
DEBUG=True

# CORS settings
CORS_ORIGINS=*

# API keys
NVIDIA_API_KEY=your_nvidia_api_key_here

# Model settings
LLM_MODEL_ID=llama-3.1-70b
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# Image model settings
IMAGE_MODEL_ID=stable-diffusion-xl
IMAGE_SIZE=1024x1024

# Development settings
USE_MOCK_DATA=True
EOF
  fi
  print_success "Backend environment file created."
else
  print_message "Backend environment file already exists."
fi

# Frontend .env setup
if [ ! -f frontend/.env ]; then
  print_message "Creating frontend environment file..."
  if [ -f frontend/.env.example ]; then
    cp frontend/.env.example frontend/.env
  else
    cat > frontend/.env << EOF
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
  fi
  print_success "Frontend environment file created."
else
  print_message "Frontend environment file already exists."
fi

if [ "$dev_mode" = true ]; then
  # Development mode setup
  print_section "BACKEND SETUP"
  cd backend || exit
  
  # Create virtual environment
  print_message "Creating Python virtual environment..."
  python3 -m venv venv
  
  # Activate virtual environment
  if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
  else
    source venv/bin/activate
  fi
  
  # Install dependencies
  print_message "Installing backend dependencies..."
  pip install -r requirements.txt
  
  # Deactivate virtual environment for now (will be reactivated when running)
  deactivate
  
  cd ..
  
  # Frontend setup
  print_section "FRONTEND SETUP"
  cd frontend || exit
  
  print_message "Installing frontend dependencies..."
  npm install
  
  print_message "Installing Tailwind CSS and related dependencies..."
  npm install -D tailwindcss postcss autoprefixer
  
  cd ..
  
  print_section "SETUP COMPLETE"
  print_success "Development environment setup completed successfully!"
  
  # Running the application
  print_section "RUNNING THE APPLICATION"
  
  read -p "Do you want to run the application now? [y/N]: " run_now
  if [[ $run_now =~ ^[Yy]$ ]]; then
    print_message "Starting backend and frontend services..."
    
    # Start backend in background
    print_message "Starting backend server..."
    cd backend || exit
    source venv/bin/activate
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    deactivate
    cd ..
    
    # Start frontend
    print_message "Starting frontend server..."
    cd frontend || exit
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    print_success "Services started successfully!"
    print_success "Backend running at: http://localhost:8000"
    print_success "Frontend running at: http://localhost:3000"
    print_success "API documentation at: http://localhost:8000/docs"
    
    print_message "Press Ctrl+C to stop all services..."
    
    # Catch interrupt signal to properly shutdown servers
    trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
  else
    print_section "HOW TO RUN"
    echo "To run the backend:"
    echo "  cd backend"
    echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "To run the frontend (in a separate terminal):"
    echo "  cd frontend"
    echo "  npm run dev"
    echo ""
    print_success "Access the application at: http://localhost:3000"
    print_success "Access the API at: http://localhost:8000"
    print_success "API documentation at: http://localhost:8000/docs"
  fi
  
else
  # Docker mode setup
  print_section "DOCKER SETUP"
  
  print_message "Building and starting Docker containers..."
  docker-compose up -d --build
  
  if [ $? -eq 0 ]; then
    print_success "Docker containers started successfully!"
    print_success "Frontend running at: http://localhost:3000"
    print_success "Backend running at: http://localhost:8000"
    print_success "API documentation at: http://localhost:8000/docs"
    
    # Test backend health
    print_message "Testing backend health endpoint..."
    sleep 5  # Wait for backend to fully start
    
    if command -v curl &> /dev/null; then
      response=$(curl -s http://localhost:8000)
      if [[ $response == *"healthy"* ]]; then
        print_success "Backend health check passed!"
      else
        print_error "Backend health check failed. Response: $response"
      fi
    else
      print_message "curl not found, skipping backend health check."
    fi
    
    print_section "DOCKER COMMANDS"
    echo "To view container logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To stop containers:"
    echo "  docker-compose down"
    echo ""
    echo "To restart containers:"
    echo "  docker-compose restart"
  else
    print_error "Failed to start Docker containers. Please check the error messages above."
    exit 1
  fi
fi

print_section "END-TO-END TESTING"
echo "Open your browser and navigate to http://localhost:3000"
echo "1. Click on 'Content Generator' to test content generation"
echo "2. Enter a topic (e.g., 'Photosynthesis') and select an audience level"
echo "3. Click 'Generate Content' and verify the response"
echo ""
echo "To try Deep Research:"
echo "1. Click on 'Deep Research' from the home page"
echo "2. Test the research functionality"
echo ""
print_success "Setup and test instructions completed." 