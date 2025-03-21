#!/bin/bash

# Setup script for EduAI project

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

print_message "Setting up EduAI project..."

# Create environment files if they don't exist
if [ ! -f backend/.env ]; then
  print_message "Creating backend environment file..."
  cp backend/.env.example backend/.env
  print_success "Backend environment file created."
else
  print_message "Backend environment file already exists."
fi

if [ ! -f frontend/.env ]; then
  print_message "Creating frontend environment file..."
  cp frontend/.env.example frontend/.env
  print_success "Frontend environment file created."
else
  print_message "Frontend environment file already exists."
fi

# Build and start containers
print_message "Building and starting Docker containers..."
docker-compose up -d --build

if [ $? -eq 0 ]; then
  print_success "EduAI is now running!"
  print_success "Frontend: http://localhost:3000"
  print_success "Backend API: http://localhost:8000"
  print_success "API Documentation: http://localhost:8000/docs"
else
  print_error "Failed to start Docker containers. Please check the error messages above."
  exit 1
fi

print_message "Setup complete! You can now use EduAI."
