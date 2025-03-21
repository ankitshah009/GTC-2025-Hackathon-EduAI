#!/bin/bash

# EduAI Run Script
# This script makes it easy to run the EduAI application (frontend, backend, or both)

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Print formatted messages
print_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
  echo -e "\n${BOLD}${PURPLE}===== $1 =====${NC}\n"
}

# Check if needed commands exist
check_requirements() {
  print_info "Checking requirements..."
  
  if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    exit 1
  fi
  
  if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
  fi
  
  if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
  fi
  
  print_success "All requirements satisfied!"
}

# Check if backend dependencies are installed
check_backend_deps() {
  if [ ! -d "backend/venv" ]; then
    print_warning "Python virtual environment not found. You might need to run setup.sh first."
    return 1
  fi
  return 0
}

# Check if frontend dependencies are installed
check_frontend_deps() {
  if [ ! -d "frontend/node_modules" ]; then
    print_warning "Node modules not found. You might need to run setup.sh or 'npm install' in the frontend directory."
    return 1
  fi
  return 0
}

# Kill existing processes
kill_processes() {
  print_info "Checking for existing processes..."
  
  # Kill uvicorn/backend processes
  if pgrep -f "uvicorn main:app" > /dev/null; then
    print_warning "Killing existing backend processes..."
    pkill -f "uvicorn main:app"
    sleep 1
  fi
  
  # Kill next.js/frontend processes
  if pgrep -f "next dev" > /dev/null; then
    print_warning "Killing existing frontend processes..."
    pkill -f "next dev"
    sleep 1
  fi
  
  print_success "All existing processes killed."
}

# Run backend server
run_backend() {
  print_header "STARTING BACKEND SERVER"
  
  if ! check_backend_deps; then
    print_warning "Proceeding anyway..."
  fi
  
  print_info "Starting backend server on port 8000..."
  cd backend || exit
  
  # Set USE_MOCK_DATA to False explicitly in environment
  export USE_MOCK_DATA=False
  print_info "Setting USE_MOCK_DATA=False to use real API"
  
  # Activate virtual environment and run server
  if [ -d "venv" ]; then
    source venv/bin/activate
    python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
    BACKEND_PID=$!
    cd ..
    print_success "Backend server started with PID: $BACKEND_PID"
    print_info "Backend running at: http://127.0.0.1:8000"
    print_info "API documentation at: http://127.0.0.1:8000/docs"
    return 0
  else
    cd ..
    print_error "Virtual environment not found. Please run setup.sh first."
    return 1
  fi
}

# Run frontend server
run_frontend() {
  print_header "STARTING FRONTEND SERVER"
  
  if ! check_frontend_deps; then
    print_warning "Proceeding anyway..."
  fi
  
  print_info "Starting frontend server on port 3000..."
  cd frontend || exit
  npm run dev &
  FRONTEND_PID=$!
  cd ..
  
  print_success "Frontend server started with PID: $FRONTEND_PID"
  print_info "Frontend running at: http://localhost:3000"
  return 0
}

# Show usage
show_usage() {
  echo -e "${BOLD}Usage:${NC} ./run.sh [options]"
  echo ""
  echo -e "${BOLD}Options:${NC}"
  echo "  -h, --help       Show this help message"
  echo "  -f, --frontend   Run only the frontend server"
  echo "  -b, --backend    Run only the backend server"
  echo "  -k, --kill       Kill existing processes only"
  echo "  -m, --mock       Force use of mock data (sets USE_MOCK_DATA=True)"
  echo ""
  echo "If no options are provided, both frontend and backend servers will be started."
}

# Main execution
main() {
  check_requirements
  
  # Parse command line arguments
  RUN_FRONTEND=false
  RUN_BACKEND=false
  USE_MOCK=false
  
  # If no arguments, run both
  if [ $# -eq 0 ]; then
    RUN_FRONTEND=true
    RUN_BACKEND=true
  fi
  
  # Process arguments
  while [ $# -gt 0 ]; do
    case "$1" in
      -h|--help)
        show_usage
        exit 0
        ;;
      -f|--frontend)
        RUN_FRONTEND=true
        ;;
      -b|--backend)
        RUN_BACKEND=true
        ;;
      -k|--kill)
        kill_processes
        exit 0
        ;;
      -m|--mock)
        USE_MOCK=true
        ;;
      *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
    esac
    shift
  done
  
  # Kill existing processes
  kill_processes
  
  # Configure mock mode if requested
  if [ "$USE_MOCK" = true ]; then
    print_header "CONFIGURING MOCK MODE"
    if grep -q "USE_MOCK_DATA: bool = False" backend/config/settings.py; then
      print_info "Setting USE_MOCK_DATA to True (temporary)..."
      sed -i.bak 's/USE_MOCK_DATA: bool = False/USE_MOCK_DATA: bool = True/g' backend/config/settings.py
      print_success "Mock mode enabled!"
    else
      print_warning "Could not configure mock mode (setting not found)"
    fi
  else
    # Ensure we're using the real API
    if grep -q "USE_MOCK_DATA: bool = True" backend/config/settings.py; then
      print_info "Setting USE_MOCK_DATA to False (using real API)..."
      sed -i.bak 's/USE_MOCK_DATA: bool = True/USE_MOCK_DATA: bool = False/g' backend/config/settings.py
      print_success "Real API mode enabled!"
    fi
  fi
  
  # Start requested services
  if [ "$RUN_BACKEND" = true ]; then
    run_backend
  fi
  
  if [ "$RUN_FRONTEND" = true ]; then
    run_frontend
  fi
  
  if [ "$RUN_BACKEND" = true ] || [ "$RUN_FRONTEND" = true ]; then
    print_header "SERVICES STARTED"
    print_info "Press Ctrl+C to stop all services..."
    
    # Keep script running to capture Ctrl+C
    trap "print_warning 'Stopping all services...'; kill \$(jobs -p) 2>/dev/null; print_success 'All services stopped.'; exit 0" INT
    wait
  fi
}

# Execute main function
main "$@"
